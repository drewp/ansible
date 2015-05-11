#!/usr/bin/python
import os, sys, json

secretsPath = os.path.join(os.path.dirname(sys.argv[0]), 'secrets.json')
secrets = json.load(open(secretsPath))

host = sys.argv[1]
print json.dumps(
    {
        "addr":"127.0.0.1",
        "port":11234,
        "password": secrets['host'][host]['adminPassword'],
    },
    sort_keys=True,
    indent=4)
