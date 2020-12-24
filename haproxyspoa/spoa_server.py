import asyncio
import functools
import logging
from collections import defaultdict
from typing import List

from haproxyspoa.payloads.ack import AckPayload
from haproxyspoa.payloads.agent_disconnect import DisconnectStatusCode, AgentDisconnectPayload
from haproxyspoa.payloads.agent_hello import AgentHelloPayload, AgentCapabilities
from haproxyspoa.payloads.haproxy_disconnect import HaproxyDisconnectPayload
from haproxyspoa.payloads.haproxy_hello import HaproxyHelloPayload
from haproxyspoa.payloads.notify import NotifyPayload
from haproxyspoa.spoa_frame import Frame, AgentHelloFrame, FrameType


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
        haproxy_hello_frame = await Frame.read_frame(reader)
        if not haproxy_hello_frame.headers.is_haproxy_hello():
            await self.send_agent_disconnect(writer)
            return
        await self.handle_hello_handshake(haproxy_hello_frame, writer)

        if HaproxyHelloPayload(haproxy_hello_frame.payload).healthcheck():
            logging.info("It is just a health check, immediately disconnecting")
            return

        logging.info("Completed new handshake with Haproxy")

        while True:
            frame = await Frame.read_frame(reader)

            if frame.headers.is_haproxy_disconnect():
                await self.handle_haproxy_disconnect(frame)
                await self.send_agent_disconnect(writer)
                return
            elif frame.headers.is_haproxy_notify():
                await self.handle_haproxy_notify(frame, writer)

    async def handle_haproxy_notify(self, frame: Frame, writer: asyncio.StreamWriter):
        notify_payload = NotifyPayload(frame.payload)

        response_futures = []
        for msg_key, msg_val in notify_payload.messages.items():
            for handler in self.handlers[msg_key]:
                response_futures.append(handler(**notify_payload.messages[msg_key]))

        ack_payloads: List[AckPayload] = await asyncio.gather(*response_futures)
        ack = AckPayload.create_from_all(*ack_payloads)

        ack_frame = Frame(
            frame_type=FrameType.ACK,
            stream_id=frame.headers.stream_id,
            frame_id=frame.headers.frame_id,
            flags=1,
            payload=ack.to_bytes()
        )
        await ack_frame.write_frame(writer)

    async def send_agent_disconnect(self, writer: asyncio.StreamWriter):
        disconnect_frame = Frame(
            frame_type=FrameType.AGENT_DISCONNECT,
            flags=1,
            stream_id=0,
            frame_id=0,
            payload=AgentDisconnectPayload().to_buffer()
        )
        await disconnect_frame.write_frame(writer)

    async def handle_haproxy_disconnect(self, frame: Frame):
        payload = HaproxyDisconnectPayload(frame.payload)
        if payload.status_code() != DisconnectStatusCode.NORMAL:
            logging.info(f"Haproxy is disconnecting us with status code {payload.status_code()} - `{payload.message()}`")

    async def handle_hello_handshake(self, frame: Frame, writer: asyncio.StreamWriter):
        agent_hello_frame = AgentHelloFrame(
            payload=AgentHelloPayload(
                capabilities=AgentCapabilities()
            ),
            stream_id=frame.headers.stream_id,
            frame_id=frame.headers.frame_id,
        )
        await agent_hello_frame.write_frame(writer)

    async def _run(self, host: str = "0.0.0.0", port: int = 9002):
        server = await asyncio.start_server(self.handle_connection, host=host, port=port, )
        await server.serve_forever()

    def run(self, *args, **kwargs):
        asyncio.run(self._run(*args, **kwargs))
