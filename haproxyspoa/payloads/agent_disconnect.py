import io
import enum

from haproxyspoa.spoa_data_types import write_typed_uint32, write_typed_string
from haproxyspoa.spoa_payloads import write_kv_list


class DisconnectStatusCode(enum.IntEnum):
    NORMAL = 0
    IO_ERROR = 1
    TIMEOUT = 2
    FRAME_TOO_BIG = 3
    INVALID_FRAME = 4
    VERSION_VALUE_NOT_FOUND = 5
    MAX_FRAME_SIZE_VALUE_NOT_FOUND = 6
    CAPABILITIES_VALUE_NOT_FOUND = 7
    UNSUPPORTED_VERSION = 8
    MAX_FRAME_SIZE_TOO_BIG_OR_TOO_SMALL = 9
    PAYLOAD_FRAGMENTATION_UNSUPPORTED = 10
    INVALID_INTERLACED_FRAMES = 11
    FRAME_ID_NOT_FOUND = 12
    RESOURCE_ALLOCATION_ERROR = 13
    UNKNOWN_ERROR = 99


class AgentDisconnectPayload:

    def __init__(self, status_code: DisconnectStatusCode = DisconnectStatusCode.NORMAL, message=""):
        self.status_code = status_code
        self.message = message

    def to_buffer(self) -> io.BytesIO:
        buffer = io.BytesIO()
        buffer.write(write_kv_list({
            "status-code": write_typed_uint32(self.status_code),
            "message": write_typed_string(self.message)
        }))
        return buffer