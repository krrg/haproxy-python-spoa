import asyncio

from haproxyspoa.spoa_frame import Frame
from haproxyspoa.spoa_payloads import HaproxyHelloPayload


class SpoaServer:

    async def handle_connection(self, reader, writer):
        frame = await Frame.read_frame(reader)

        print(f"Stream ID: {frame.stream_id}")
        print(f"Frame ID: {frame.frame_id}")
        print(f"Frame Type: {frame.type}")
        print(f"Frame Payload Length: {len(frame.payload.getvalue())}")

        payload = HaproxyHelloPayload(frame.payload)

        print(payload.attrs)

        print("supported versions", payload.supported_versions())
        print("max frame size", payload.max_frame_size())
        print("capabilities", payload.capabilities())
        print("healthcheck", payload.healthcheck())
        print("engine-id", payload.engine_id())

    async def run(self, host: str = "0.0.0.0", port: int = 9002):
        server = await asyncio.start_server(self.handle_connection, host=host, port=port)
        await server.serve_forever()

