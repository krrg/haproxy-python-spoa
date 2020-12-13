import io

from haproxyspoa.spoa_payloads import parse_kv_list


class HaproxyDisconnectPayload:

    def __init__(self, payload: io.BytesIO):
        self.kv_list = parse_kv_list(payload)

    def status_code(self) -> int:
        return int(self.kv_list.get("status-code"))

    def message(self) -> str:
        return self.kv_list.get("message")
