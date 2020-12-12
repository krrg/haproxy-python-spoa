import asyncio
import io

from haproxyspoa.payloads.actions import ActionsPayload
from haproxyspoa.payloads.agent_hello import AgentHelloPayload
from haproxyspoa.spoa_data_types import parse_varint, write_varint


class FrameType:
    FRAGMENT = 0
    HAPROXY_HELLO = 1
    HAPROXY_DISCONNECT = 2
    HAPROXY_NOTIFY = 3
    AGENT_HELLO = 101
    AGENT_DISCONNECT = 102
    ACK = 103


class FrameHeaders:

    def __init__(
        self,
        frame_type: int,
        flags: int,
        stream_id: int,
        frame_id: int,
    ):
        self.type = frame_type
        self.flags = flags
        self.stream_id = stream_id
        self.frame_id = frame_id

    def is_fragmented_or_unset(self):
        # Note: This implementation doesn't support fragmented frames, so
        #  if the frame is fragmented, we're toast.
        return self.type == FrameType.FRAGMENT

    def is_haproxy_hello(self):
        return self.type == FrameType.HAPROXY_HELLO

    def is_haproxy_disconnect(self):
        return self.type == FrameType.HAPROXY_DISCONNECT

    def is_haproxy_notify(self):
        return self.type == FrameType.HAPROXY_NOTIFY

    def is_agent_hello(self):
        return self.type == FrameType.AGENT_HELLO

    def is_agent_disconnect(self):
        return self.type == FrameType.AGENT_DISCONNECT

    def is_ack(self):
        return self.type == FrameType.ACK


class Frame:

    def __init__(
        self,
        frame_type: int,
        flags: int,
        stream_id: int,
        frame_id: int,
        payload: io.BytesIO,
    ):
        self.headers = FrameHeaders(
            frame_type,
            flags,
            stream_id,
            frame_id
        )
        self.payload = payload

    @staticmethod
    async def read_frame(reader: asyncio.StreamReader):
        frame_length = int.from_bytes(await reader.readexactly(4), byteorder='big', signed=False)
        frame_bytes: bytes = await reader.readexactly(frame_length)
        frame_bytesio = io.BytesIO(frame_bytes)

        frame_type = int.from_bytes(frame_bytesio.read(1), byteorder='big', signed=False)
        flags = int.from_bytes(frame_bytesio.read(4), byteorder='big', signed=False)
        stream_id = parse_varint(frame_bytesio)
        frame_id = parse_varint(frame_bytesio)

        return Frame(
            frame_type,
            flags,
            stream_id,
            frame_id,
            frame_bytesio
        )

    async def write_frame(self, writer: asyncio.StreamWriter):
        header_buffer = io.BytesIO()

        header_buffer.write(self.headers.type.to_bytes(1, byteorder='big'))
        header_buffer.write(self.headers.flags.to_bytes(4, byteorder='big'))
        header_buffer.write(write_varint(self.headers.stream_id))
        header_buffer.write(write_varint(self.headers.frame_id))

        frame_header_bytes = header_buffer.getvalue()
        frame_payload_bytes = self.payload.getvalue()
        frame_length = len(frame_header_bytes) + len(frame_payload_bytes)

        writer.write(frame_length.to_bytes(4, byteorder='big'))
        writer.write(frame_header_bytes)
        writer.write(frame_payload_bytes)
        await writer.drain()


class AgentHelloFrame(Frame):

    def __init__(self,  payload: AgentHelloPayload, flags: int = 1, stream_id: int = 0, frame_id: int = 0):
        super().__init__(
            FrameType.AGENT_HELLO,
            flags,
            stream_id,
            frame_id,
            io.BytesIO(payload.to_bytes())
        )


