FROM alpine:3.5

RUN apk --no-cache add dnsmasq bash

EXPOSE 53 53/udp

ENTRYPOINT ["dnsmasq", "--conf-file=/opt/dnsmasq/dnsmasq.conf"]
