import asyncio
import io

from haproxyspoa.spoa_data_types import parse_varint, parse_string


class FrameType:
    FRAGMENT = 0
    HAPROXY_HELLO = 1
    HAPROXY_DISCONNECT = 2
    HAPROXY_NOTIFY = 3
    AGENT_HELLO = 101
    AGENT_DISCONNECT = 102
    ACK = 103


class Frame:

    def __init__(
        self,
        frame_type: int,
        flags: int,
        stream_id: int,
        frame_id: int,
        payload: io.BytesIO,
    ):
        self.type = frame_type
        self.flags = flags
        self.stream_id = stream_id
        self.frame_id = frame_id
        self.payload = payload

        placeholder = payload.tell()
        print(payload.read())
        payload.seek(placeholder)

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





