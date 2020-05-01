#!/bin/zsh

EXT=ens4
WIFI=ens5
INT=enp1s0
WIFI_NET=10.2.0.0/16
BANG_10_1=10.1.0.1
BANG_10_2=10.2.0.1
DOCKER_NET=172.16.0.0/12
WIREGUARD_NET=10.5.0.0/16

ufw logging low
ufw disable
ufw --force reset

# part 1
ufw allow in on ${WIFI} proto udp to any port 67 comment dhcp
ufw allow in on ${WIFI} proto udp to any port 68 comment dhcp

ufw allow in on ${WIFI} proto udp to any port 53 comment dns
ufw allow in on ${INT} proto udp to any port 53 comment dns

ufw allow in on ${WIFI} proto tcp to ${BANG_10_2} port 8443 comment mitmproxy

ufw allow in on ${WIFI} proto tcp to ${BANG_10_2} port ssh comment ssh

ufw allow from ${WIFI_NET} to ${BANG_10_2} port 1195 proto udp comment wireguard
ufw allow from ${WIREGUARD_NET}

ufw allow proto tcp to any port http comment http
ufw allow proto tcp to any port https comment https

ufw allow from ${DOCKER_NET} comment 'from docker'

# part 2
ufw deny in on ${WIFI} to ${BANG_10_2} # with exceptions above

# part 3
ufw route deny in on ${EXT} comment 'protect from outside'
ufw route deny in on ${WIFI} out on ${INT} comment 'protect 10.1'

ufw route allow in on ${INT}
ufw allow in on ${INT} to any

ufw --force enable

ufw status verbose
