import asyncio
import functools
from collections import defaultdict
from typing import List

from haproxyspoa.logging import logger, FlowIdLoggerAdapter
from haproxyspoa.payloads.ack import AckPayload
from haproxyspoa.payloads.agent_disconnect import DisconnectStatusCode, AgentDisconnectPayload
from haproxyspoa.payloads.agent_hello import AgentHelloPayload, AgentCapabilities
from haproxyspoa.payloads.haproxy_disconnect import HaproxyDisconnectPayload
from haproxyspoa.payloads.haproxy_hello import HaproxyHelloPayload
from haproxyspoa.payloads.notify import NotifyPayload
from haproxyspoa.spoa_frame import Frame, AgentHelloFrame, FrameType

import secrets


class SpoaConnection:
    
    def __init__(self, writer: asyncio.StreamWriter, handlers):
        self.logger = FlowIdLoggerAdapter(logger, {"flow_id": secrets.token_hex(4)})
        self.handlers = handlers
        self.writer = writer

    async def handle_haproxy_notify(self, frame: Frame):
        self.logger.debug("Incoming `notify` frame from HAProxy")
        notify_payload = NotifyPayload(frame.payload)

        response_futures = []
        for msg_key, msg_val in notify_payload.messages.items():
            self.logger.info(f"Received request on key '{msg_key}'")
            for handler in self.handlers[msg_key]:
                response_futures.append(handler(**notify_payload.messages[msg_key]))

        self.logger.info(f"Found {len(response_futures)} matching handlers, awaiting response...")
        ack_payloads: List[AckPayload] = await asyncio.gather(*response_futures)
        ack = AckPayload.create_from_all(*ack_payloads)
        payload = ack.to_bytes()

        self.logger.info(f"Responding with combined payload of {len(payload.getbuffer())} bytes")

        ack_frame = Frame(
            frame_type=FrameType.ACK,
            stream_id=frame.headers.stream_id,
            frame_id=frame.headers.frame_id,
            flags=1,
            payload=payload
        )
        await ack_frame.write_frame(self.writer)

    async def send_agent_disconnect(self):
        self.logger.info("Agent is now dropping connection")
        disconnect_frame = Frame(
            frame_type=FrameType.AGENT_DISCONNECT,
            flags=1,
            stream_id=0,
            frame_id=0,
            payload=AgentDisconnectPayload().to_buffer()
        )
        await disconnect_frame.write_frame(self.writer)

    async def handle_haproxy_disconnect(self, frame: Frame):
        payload = HaproxyDisconnectPayload(frame.payload)
        if payload.status_code() != DisconnectStatusCode.NORMAL:
            self.logger.info(f"Haproxy is disconnecting us with status code {payload.status_code()} - `{payload.message()}`")

    async def handle_hello_handshake(self, frame: Frame):
        capabilities = AgentCapabilities()
        self.logger.info(f"Received `hello handshake`, responding with agent capabilities of: '{capabilities}'")
        agent_hello_frame = AgentHelloFrame(
            payload=AgentHelloPayload(
                capabilities=capabilities,
            ),
            stream_id=frame.headers.stream_id,
            frame_id=frame.headers.frame_id,
        )
        await agent_hello_frame.write_frame(self.writer)


class SpoaServer:

    def __init__(self):
        self.handlers = defaultdict(list)

    def handler(self, message_key: str):
        def _handler(fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                return fn(*args, **kwargs)
            self.handlers[message_key].append(wrapper)
            return wrapper
        return _handler

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        conn = SpoaConnection(writer, self.handlers)
        
        haproxy_hello_frame = await Frame.read_frame(reader)

        if not haproxy_hello_frame.headers.is_haproxy_hello():
            conn.logger.error(f"""
                Expected a `hello` frame from HAProxy,
                but received unexpected frame of type {haproxy_hello_frame.headers.frame_type}
            """.strip())
            await conn.send_agent_disconnect()
            return
        await conn.handle_hello_handshake(haproxy_hello_frame)

        if HaproxyHelloPayload(haproxy_hello_frame.payload).healthcheck():
            conn.logger.info("Health check, immediately disconnecting")
            return

        while True:
            frame = await Frame.read_frame(reader)

            if frame.headers.is_haproxy_disconnect():
                await conn.handle_haproxy_disconnect(frame)
                await conn.send_agent_disconnect()
                return
            elif frame.headers.is_haproxy_notify():
                await conn.handle_haproxy_notify(frame)

    async def _run(self, host: str = "0.0.0.0", port: int = 9002):
        server = await asyncio.start_server(self.handle_connection, host=host, port=port, )
        logger.info(f"HAProxy SPO Agent listening at {host}:{port}")
        await server.serve_forever()

    def run(self, *args, **kwargs):
        asyncio.run(self._run(*args, **kwargs))
