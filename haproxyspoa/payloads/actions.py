import io

from haproxyspoa.spoa_payloads import parse_list_of_actions


class ActionsPayload:

    def __init__(self, payload: io.BytesIO):
        actions_list = parse_list_of_actions(payload)
        print(actions_list)



