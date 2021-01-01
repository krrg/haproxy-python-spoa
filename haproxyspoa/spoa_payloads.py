import io
from collections import defaultdict
from typing import Dict

from haproxyspoa.spoa_data_types import parse_string, parse_typed_data, write_string, write_typed_autodetect


def parse_list_of_messages(payload: io.BytesIO) -> dict:
    messages = {}

    while payload.tell() != len(payload.getbuffer()):
        message_name = parse_string(payload)
        num_args = int.from_bytes(payload.read(1), byteorder='little', signed=False)

        arguments = defaultdict(list)
        for _ in range(num_args):
            key, value = parse_key_value_pair(payload)
            arguments[key].append(value)

        # For convenience in the handlers, flatten arguments
        #  that have only one value mapping to the same key.
        for argkey in arguments.keys():
            if len(arguments[argkey]) == 1:
                arguments[argkey] = arguments[argkey][0]

        messages[message_name] = arguments

    # Hide the default dict implementation
    for k in messages.keys():
        messages[k] = dict(messages[k])

    return messages


def parse_key_value_pair(payload: io.BytesIO):
    key = parse_string(payload)
    value = parse_typed_data(payload)
    return key, value


class Action:

    SET_VAR = 1
    UNSET_VAR = 2

    def __init__(self, _type: int, args: int):
        self.type = _type,
        self.args = args


def write_list_of_actions(actions: list) -> bytes:
    buffer = io.BytesIO()

    for action in actions:
        _type = bytes([action.type])
        num_args = bytes([len(action.args)])

        buffer.write(_type)
        buffer.write(num_args)

        for arg in action.args:
            buffer.write(write_typed_autodetect(arg))

    return buffer.getvalue()


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
