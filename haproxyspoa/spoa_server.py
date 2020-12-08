import asyncio

from haproxyspoa.payloads.agent_hello import AgentHelloPayload, AgentCapabilities
from haproxyspoa.spoa_frame import Frame, AgentHelloFrame
from haproxyspoa.payloads.haproxy_hello import HaproxyHelloPayload



class SpoaServer:

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        haproxy_hello_frame = await Frame.read_frame(reader)
        payload = HaproxyHelloPayload(haproxy_hello_frame.payload)

        agent_hello_frame = AgentHelloFrame(
            payload=AgentHelloPayload(
                capabilities=AgentCapabilities()
            ),
            stream_id=haproxy_hello_frame.stream_id,
            frame_id=haproxy_hello_frame.frame_id,
        )
        await agent_hello_frame.write_frame(writer)

        next_unknown_frame = await Frame.read_frame(reader)
        print("The next frame is of type: ", next_unknown_frame.type)
        print("The payload is: ", next_unknown_frame.payload.read())


    async def run(self, host: str = "0.0.0.0", port: int = 9002):
        server = await asyncio.start_server(self.handle_connection, host=host, port=port)
        await server.serve_forever()

