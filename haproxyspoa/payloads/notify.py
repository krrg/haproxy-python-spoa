import io

from haproxyspoa.spoa_payloads import parse_list_of_messages


class NotifyPayload:

    def __init__(self, payload: io.BytesIO):
        self.messages = parse_list_of_messages(payload)

