import io

from haproxyspoa.spoa_payloads import parse_kv_list


class HaproxyHelloPayload:

    def __init__(self, payload: io.BytesIO):
        self.attrs = parse_kv_list(payload)

    def supported_versions(self):
        return self.attrs["supported-versions"].replace(" ", "").split(",")

    def max_frame_size(self):
        return self.attrs["max-frame-size"]

    def capabilities(self):
        return self.attrs["capabilities"].replace(" ", "").split(",")

    def healthcheck(self) -> bool:
        return self.attrs.get("healthcheck", False)

    def engine_id(self):
        return self.attrs.get("engine-id", None)