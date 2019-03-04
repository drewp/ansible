import subprocess
import time
from influxdb import InfluxDBClient
client = InfluxDBClient(host='bang', port=9060, database='network')
client.create_database('network')
client.create_retention_policy('1h', database='network', replication='1', duration='1h')

def parse_bytes(s):
    try:
        if s.endswith('Mb'):
            return int(s.strip('Mb')) * 1024 * 1024
        if s.endswith('Kb') or s.endswith('K'):
            return int(s.strip('Kb')) * 1024
        if s.endswith('b'):
            return int(s[:-1])
        raise ValueError()
    except ValueError:
        print(f's = {s}')
        raise
    
def poll():
    class_name = 'unset'
    now = int(time.time())
    points = []
    tags = {}

    for line in subprocess.check_output(["tc", "-s", "class", "show", "dev", "ens5"]).splitlines():
        words = line.strip().decode('ascii').split()
        if not words:
            continue
        if words[0:2] == ['class', 'hfsc']:
            class_code = words[2]
            class_name = {'1:': 'root',
                          '1:1': 'main_rate_limit',
                          '1:2': 'interactive',
                          '1:3': 'voip',
                          '1:4': 'browsing',
                          '1:5': 'default',
                          '1:6': 'low',
            }[class_code]
            tags = {'class_name': class_name}
        if words[0] == 'Sent':
            points.append({'measurement': 'bytes', "tags": tags, "fields": {"sent": int(words[1])}, "time": now})
            points.append({'measurement': 'packets', "tags": tags, "fields": {"sent": int(words[3]),
                                                                              'dropped': int(words[6].rstrip(',')),
                                                                              'overlimits': int(words[8]),
                                                                              'requeues': int(words[10].rstrip(')')),
                                                                          }, "time": now})

        if words[0] == 'backlog':
            points.append({'measurement': 'bytes', "tags": tags, "fields": {"backlog": parse_bytes(words[1])}, "time": now})

            points.append({'measurement': 'packets', "tags": tags, "fields": {
                'backlog_packets': int(words[2].rstrip('p')),
                'backlog_requeues': int(words[4]),
            }, "time": now})
        if words[0] == 'period':
            points.append({'measurement': 'period', "tags": tags, "fields": {"period": int(words[1])}, "time": now})


            if words[2] == 'work':
                points.append({'measurement': 'bytes', "tags": tags, "fields": {"work": int(words[3])}, "time": now})
                if words[5] == 'rtwork':
                    points.append({'measurement': 'bytes', "tags": tags, "fields": {"rtwork": int(words[6])}, "time": now})

            # print 'level', class_name, words[-1] #??



    client.write_points(points, database='network', retention_policy='1h', time_precision='s')

while True:
    poll()
    time.sleep(2)
