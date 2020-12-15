FROM haproxy:latest

COPY haproxy/ /usr/local/etc/haproxy/

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["haproxy", "-d", "-f", "/usr/local/etc/haproxy"]