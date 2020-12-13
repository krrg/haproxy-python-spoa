FROM haproxy:2.2

COPY haproxy/ /usr/local/etc/haproxy/

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["haproxy", "-d", "-f", "/usr/local/etc/haproxy"]