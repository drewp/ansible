#!/usr/bin/python
"""
to start a host, run this:
./cjdroute --genconf >> /tmp/cjdroute.conf
then copy lines into secrets.json:
  "publicKey": "....k",
  "ipv6": "...",
  "privateKey": "..."
"""


import json, sys, string, os
from Crypto.Random import random

publicPort = 9878
secretsPath = os.path.join(os.path.dirname(sys.argv[0]), 'secrets.json')
secrets = json.load(open(secretsPath))

def getConfig(host):
    sh = secrets['host'][host]
    auths = []
    if 'publicAddress' in sh:
        for otherHost, oh in secrets['host'].items():
            if otherHost == host:
                continue
            auths.append({'password': getConnectPassword(otherHost, host)})

    publicConnections = {}
    for otherHost, oh in secrets['host'].items():
        if otherHost == host:
            continue
        if 'publicAddress' in oh:
            publicConnections['%s:%s' % (oh['publicAddress'], publicPort)] = {
                'password': getConnectPassword(host, otherHost),
                'publicKey': oh['publicKey'],
            }

    eths = []
    for iface in sh.get('localInterfaces', []):
        eths.append({
            "bind": iface,
            "beacon": 2, # or, pick one leader for the LAN
        })
    return {
        'privateKey': sh['privateKey'],
        'publicKey': sh['publicKey'],
        'ipv6': sh['ipv6'],
        'authorizedPasswords': auths,
        'admin': {
            'bind': "127.0.0.1:11234",
            'password': sh['adminPassword'],
            },
        'interfaces': {
            'UDPInterface': [{
                'bind': '0.0.0.0:%s' % publicPort,
                'connectTo': publicConnections,
                }],
            'ETHInterface': eths,
        },
        "router": {
            "interface": {
                "type": "TUNInterface"
            },
        },
        "resetAfterInactivitySeconds": 100,
        "security": [
            {
                "setuser": "nobody",
                "exemptAngel": 1
            }
        ],
        "logging": {
            "logTo":"admin"
        },
        "noBackground":1,
    }

def getConnectPassword(fromHost, toHost):
    """
    password is used in connectTo on fromHost's config and as an
    authorizedPassword in toHost's config. Adds to secrets.json if
    necessary.
    """
    th = secrets['host'][toHost]
    try:
        return th['passwordFrom'][fromHost]
    except KeyError:
        pass
    password = '%s-%s-%s' % (fromHost, toHost, ''.join(random.choice(string.printable[:10+26+26])
                                                       for i in range(64)))
    th.setdefault('passwordFrom', {})[fromHost] = password
    with open(secretsPath, 'w') as out:
        json.dump(secrets, out, indent=4, sort_keys=True)
    return password


print json.dumps(getConfig(sys.argv[1]), indent=4)
