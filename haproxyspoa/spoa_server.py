import asyncio

from haproxyspoa.payloads.agent_hello import AgentHelloPayload, AgentCapabilities
from haproxyspoa.payloads.haproxy_hello import HaproxyHelloPayload
from haproxyspoa.payloads.notify import NotifyPayload
from haproxyspoa.spoa_frame import Frame, AgentHelloFrame


class SpoaServer:

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        await self.handle_hello_handshake(reader, writer)

        while True:
            frame = await Frame.read_frame(reader)

            if frame.headers.is_haproxy_disconnect():
                await self.handle_haproxy_disconnect(reader, writer)
            elif frame.headers.is_haproxy_notify():
                await self.handle_haproxy_notify(frame, writer)

    async def handle_haproxy_notify(self, frame: Frame, writer: asyncio.StreamWriter):
        print(frame.headers.frame_id)
        print(frame.headers.stream_id)
        action_payload = NotifyPayload(frame.payload)

    async def send_agent_disconnect(self, writer: asyncio.StreamWriter):
        pass

    async def handle_haproxy_disconnect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        print("Haproxy is disconnecting us")
        # TODO: Send an agent-disconnect
        await self.send_agent_disconnect(writer)
        return

    async def handle_hello_handshake(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        haproxy_hello_frame = await Frame.read_frame(reader)
        payload = HaproxyHelloPayload(haproxy_hello_frame.payload)

        agent_hello_frame = AgentHelloFrame(
            payload=AgentHelloPayload(
                capabilities=AgentCapabilities()
            ),
            stream_id=haproxy_hello_frame.headers.stream_id,
            frame_id=haproxy_hello_frame.headers.frame_id,
        )
        await agent_hello_frame.write_frame(writer)

        if payload.healthcheck():
            await self.send_agent_disconnect(writer)

    async def run(self, host: str = "0.0.0.0", port: int = 9002):
        server = await asyncio.start_server(self.handle_connection, host=host, port=port, )
        await server.serve_forever()
