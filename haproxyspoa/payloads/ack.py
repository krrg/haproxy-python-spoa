import io
from enum import IntEnum
from typing import Any

from haproxyspoa.spoa_data_types import write_string, write_typed_autodetect, write_typed_string
from haproxyspoa.spoa_payloads import Action


class ActionVarScope(IntEnum):
    PROCESS = 0
    SESSION = 1
    TRANSACTION = 2
    REQUEST = 3
    RESPONSE = 4


class ActionSetVar:

    def __init__(self, scope: ActionVarScope, name: str, value: Any):
        self.scope = scope
        self.name = name
        self.value = value

    def to_bytes(self) -> bytes:
        buffer = io.BytesIO()
        buffer.write(int.to_bytes(Action.SET_VAR, 1, byteorder='big', signed=False))
        buffer.write(int.to_bytes(3, 1, byteorder='big', signed=False))  # Number of arguments
        buffer.write(int.to_bytes(int(self.scope.value), 1, byteorder='big', signed=False))
        buffer.write(write_string(self.name))  # Possibly contrary to the docs, this is not a typed string.
        buffer.write(write_typed_autodetect(self.value))
        return buffer.getvalue()


class ActionUnsetVar:

    def __init__(self, scope: ActionVarScope, name: str):
        self.scope = scope
        self.name = name

    def to_bytes(self) -> bytes:
        buffer = io.BytesIO()
        buffer.write(int.to_bytes(Action.UNSET_VAR, 1, byteorder='big', signed=False))
        buffer.write(int.to_bytes(2, 1, byteorder='big', signed=False))  # Number of arguments
        buffer.write(int.to_bytes(int(self.scope.value), 1, byteorder='big', signed=False))
        buffer.write(write_typed_string(self.name))
        return buffer.getvalue()


class AckPayload:

    def __init__(self, actions=None):
        self.actions = actions if actions is not None else []

    def set_var(self, scope: ActionVarScope, name: str, value: Any):
        self.actions.append(ActionSetVar(scope, name, value))
        return self

    def unset_var(self, scope: ActionVarScope, name: str):
        self.actions.append(ActionUnsetVar(scope, name))
        return self

    def set_txn_var(self, name: str, value: Any):
        return self.set_var(ActionVarScope.TRANSACTION, name, value)

    @staticmethod
    def create_from_all(*others: 'AckPayload'):
        actions = []
        for ack in others:
            actions.extend(ack.actions)
        return AckPayload(actions=actions)

    def to_bytes(self) -> io.BytesIO:
        buffer = io.BytesIO()
        for action in self.actions:
            buffer.write(action.to_bytes())
        return buffer


