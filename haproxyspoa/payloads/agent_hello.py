from haproxyspoa.spoa_data_types import write_typed_string, write_typed_uint32
from haproxyspoa.spoa_payloads import write_kv_list


class AgentCapabilities:

    def __init__(self):
        self.supported_list = set()

    def support_fragmentation(self):
        self.supported_list.add("fragmentation")
        return self

    def support_pipelining(self):
        self.supported_list.add("pipelining")
        return self

    def support_async(self):
        self.supported_list.add("async")
        return self


class AgentHelloPayload:
    GENEROUS_MAX_FRAME_SIZE = 65536
    DEFAULT_MAX_FRAME_SIZE = 16380

    def __init__(
            self,
            spop_version: int = 2.0,
            max_frame_size: int = DEFAULT_MAX_FRAME_SIZE,
            capabilities: AgentCapabilities = None
    ):
        self.version = spop_version
        self.max_frame_size = max_frame_size
        self.capabilities = ",".join(capabilities.supported_list) if capabilities is not None else ""

    def to_bytes(self) -> bytes:
        return write_kv_list({
            "version": write_typed_string(str(self.version)),
            "max-frame-size": write_typed_uint32(self.max_frame_size),
            "capabilities": write_typed_string(self.capabilities)
        })

