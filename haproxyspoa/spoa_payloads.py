import io

from typing import Dict, List

from collections import namedtuple, defaultdict

from haproxyspoa.spoa_data_types import parse_string, parse_typed_data, write_string


def parse_list_of_messages(payload: io.BytesIO) -> dict:
    messages = {}

    while payload.tell() != len(payload.getbuffer()):
        message_name = parse_string(payload)
        num_args = int.from_bytes(payload.read(1), byteorder='little', signed=False)

        print("The number of arguments is: ", num_args)

        arguments = defaultdict(list)
        for _ in range(num_args):
            key, value = parse_key_value_pair(payload)
            arguments[key].append(value)
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

    def __init__(self, _type, args):
        self.type = _type,
        self.args = args


def parse_list_of_actions(payload: io.BytesIO) -> List[Action]:
    # Note: the agent should never have to actually parse this...
    #  Didn't realize that until later.
    actions = []
    while payload.tell() != len(payload.getbuffer()):
        action_type = payload.read(1)[0]
        num_args = payload.read(1)[0]

        print(f"Just read action_type of {action_type}")
        print(f"This action has {num_args} number of args")

        args = list([
            parse_typed_data(payload) for _ in range(num_args)
        ])
        print("The args are as follows: ", args)
        print()
        actions.append(
            Action(action_type, args)
        )
    return actions


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
