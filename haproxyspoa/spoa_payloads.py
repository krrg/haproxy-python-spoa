import io

from typing import Dict

from haproxyspoa.spoa_data_types import parse_string, parse_typed_data, write_string


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
    raise NotImplemented("Agents do not parse actions; they only send them.")


def parse_kv_list(payload: io.BytesIO):
    kv_list = {}
    while payload.tell() != len(payload.getbuffer()):
        key = parse_string(payload)
        value = parse_typed_data(payload)
        kv_list[key] = value
    return kv_list


def write_kv_list(kv: Dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    for k, v in kv.items():
        buffer.write(write_string(k))
        buffer.write(v)
    return buffer.getvalue()

