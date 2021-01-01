from ipaddress import IPv4Address

from haproxyspoa.payloads.ack import AckPayload
from haproxyspoa.spoa_server import SpoaServer


agent = SpoaServer()


@agent.handler("earth-to-mars")
async def handle_earth_to_mars(src: IPv4Address, req_host: str):
    return AckPayload().set_txn_var("transmission_src", str(src) + req_host)


if __name__ == "__main__":
    agent.run(host='127.0.0.1', port=9002)
