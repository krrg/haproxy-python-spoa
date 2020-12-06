import io

from haproxyspoa.spoa_data_types import parse_string, parse_typed_data


def parse_list_of_messages(payload: io.BytesIO) -> dict:
    messages = {}

    while payload.tell() != len(payload.getbuffer()):
        message_name = parse_string(payload)
        num_args = int.from_bytes(payload.read(1), byteorder='little', signed=False)

        print("The number of arguments is: ", num_args)

        arguments = {}
        for _ in range(num_args):
            key, value = parse_key_value_pair(payload)
            arguments[key] = value

        messages[message_name] = arguments

    return messages


def parse_key_value_pair(payload: io.BytesIO):
    key = parse_string(payload)
    value = parse_typed_data(payload)
    return key, value


def parse_list_of_actions(payload: io.BytesIO):
    raise NotImplemented()


def parse_kv_list(payload: io.BytesIO):
    kv_list = {}
    while payload.tell() != len(payload.getbuffer()):
        print(payload.tell())
        key = parse_string(payload)
        value = parse_typed_data(payload)
        kv_list[key] = value
    return kv_list


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

