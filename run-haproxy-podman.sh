#!/bin/bash
podman build . -t haproxy-python-spoa 
podman run \
    -t -i \
    --rm \
    --network=host \
    haproxy-python-spoa 
