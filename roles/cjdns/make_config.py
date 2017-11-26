#!/usr/bin/python
"""
to start a host, run this:
./cjdroute --genconf >> /tmp/cjdroute.conf
then copy lines into secrets.json:
  "publicKey": "....k",
  "ipv6": "...",
  "privateKey": "..."
"""


import json, sys, string, subprocess
from Crypto.Random import random
from twisted.python.filepath import FilePath

publicPort = 9878
secretsPath = FilePath(sys.argv[0]).sibling('secrets.json')
secrets = json.load(secretsPath.open())

def randomString(n):
    return ''.join(random.choice(string.printable[:10+26+26]) for i in range(n))
    
def parseCjdConf(jsonish):
    confJson = ''
    lines = iter(jsonish.splitlines())
    for line in lines:
        line = line.strip()
        if line.startswith('//'):
            continue
        if line == '/*':
            while lines.next().strip() != '*/':
                pass
            continue
        #if line == '"ETHInterface":':
        #    line = ',' + line
        if line == '"noBackground":0,':
            line = '"noBackground":0'
        confJson += line + '\n'
    confJson = confJson.replace(']\n\n"', '],\n"')
    return json.loads(confJson)

def newHost(host, localInterfaces=[]):
    conf = parseCjdConf(subprocess.check_output(['/opt/cjdns/cjdroute', '--genconf']))
    return {
        "adminPassword": randomString(32),
        "ipv6": conf['ipv6'], 
        "localInterfaces": localInterfaces,
        "privateKey": conf['privateKey'], 
        "publicKey": conf['publicKey'],
    } 
    

def getConfig(host):
    try:
        sh = secrets['host'][host]
    except KeyError:
        sh = secrets['host'][host] = newHost(host)
        secretsPath.setContent(json.dumps(secrets, indent=4))
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
    password = '%s-%s-%s' % (fromHost, toHost, randomString(64))
    th.setdefault('passwordFrom', {})[fromHost] = password
    secretsPath.setContent(json.dumps(secrets, indent=4, sort_keys=True))
    return password


print json.dumps(getConfig(sys.argv[1]), indent=4)
