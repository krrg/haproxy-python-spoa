#!/bin/bash
podman build . -t haproxy-okta-gateway 
podman run \
    -t -i \
    --rm \
    --network=host \
    haproxy-okta-gateway
