# HAProxy SPOA
A pure Python implementation of an HAProxy Stream Processing Offload Agent with asyncio support.

This library handles the lower level details of the Stream Processing Offload Protocol, allowing quick implementation of custom agents.
See the `example` folder for the full example, including an example HAProxy configuration.

```python
from ipaddress import IPv4Address

from haproxyspoa.payloads.ack import AckPayload
from haproxyspoa.spoa_server import SpoaServer

agent = SpoaServer()


@agent.handler("earth-to-mars")
async def handle_earth_to_mars(src: IPv4Address, req_host: str):
    return AckPayload().set_txn_var("src_echo", str(src) + req_host)


if __name__ == "__main__":
    agent.run(host='127.0.0.1', port=9002)
```

## Installation
This library is published on PyPI, making it easy to install with `pip` or your favorite Python package manager.
```
pip install haproxyspoa
```


