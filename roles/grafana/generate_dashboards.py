

import json, itertools, os
from private import wifis, piNodes, webcamTags, pingHosts, audioHosts, camLocs, mongoDbs

null, true, false = None, True, False

nextId = itertools.count().next

def tagList(tags):
    out = []
    for k, v in tags:
        row = {'key': k, 'operator': '=', 'value': v}
        if out:
            row['condition'] = 'AND'
        out.append(row)
    return out

def metric(alias, measurement, field, tags, avg=0):
    funcs = []
    if avg:
        funcs.append({"params": [avg], "type": "moving_average"})
   
    return {
        "alias": alias,
        "dsType": "influxdb",
        "groupBy": [
            {"params": ["$__interval"], "type": "time"},
            {"params": ["null"], "type": "fill"},
        ],
        "measurement": measurement,

        "select": [
            [
                {"params": [field], "type": "field"},
                {"params": [], "type": "mean"}
            ] + funcs
        ],
        "tags": tagList(tags), 
    }

def cpu_usage_panel(process_name, hosts):
    return cpu_usage_panel_targets(process_name, [
        metric(alias=n, measurement="procstat", field="cpu_usage", tags=[('host', n), ('process_name', process_name)]) for n in hosts
    ])
    
def cpu_usage_panel_targets(process_name, targets):
    return {
        'id': nextId(),
        "title": '%s cpu percent' % process_name,
        "type": "graph",
        "span": 12,
        "datasource": "telegraf",
        "interval": ">10s",
        "yaxes": [
            {"format": "short", "min": 0, 'max': 130, 'show':true},
            {"format": "short", "min": 0, 'show':true},
        ],
        "targets": targets,
    }

def float_panel(datasource, max, title, targets):
    return {
        'id': nextId(),
        "title": title,
        "type": "graph",
        "span": 12,
        "datasource": datasource,
        "interval": ">10s",
        "yaxes": [
            {"format": "short", "min": 0, 'max': max, 'show':true},
            {"format": "short", "min": 0, 'show':true},
        ],
        "targets": targets,
    }


    
def discrete_panel(title, dtype, measurement, tags):
    ret = {
          "backgroundColor": "rgba(128, 128, 128, 0.1)",
          "datasource": "main",
          "display": "timeline",
          "expandFromQueryS": 3600,
          "extendLastValue": true,
          "highlightOnMouseover": true,
          "id": nextId(),
          "interval": ">60s",
          "legendSortBy": "-ms",
          "lineColor": "rgba(128, 128, 128, 1.0)",
          "links": [],
          "mappingTypes": [
            {"name": "value to text", "value": 1},
            {"name": "range to text", "value": 2}
          ],
          "metricNameColor": "#000000",
          "rangeMaps": [],
          "rowHeight": 25,
          "showDistinctCount": false,
          "showLegend": true,
          "showLegendCounts": false, "showLegendNames": true, "showLegendPercent": true, "showLegendTime": true, "showLegendValues": true, "showTransitionCount": true,
          "span": 12,
          "targets": [
            {"dsType": "influxdb", "groupBy": [], "measurement": measurement, "orderByTime": "ASC", "policy": "default", "refId": nextId(), "resultFormat": "time_series",
             "select": [[{"params": ["value"], "type": "field"}]],
             "tags": tagList(tags),
            }
          ],
          "textSize": 12,
          "title": title,
          "type": "natel-discrete-panel",
          "valueTextColor": "#000000",
          "writeAllValues": true,
          "writeLastValue": false,
          "writeMetricNames": false
        }

    if dtype == 'open':
        ret.update({
          "colorMaps": [{"color": "rgb(212, 150, 106)", "text": "open"}, {"color": "rgb(85, 35, 0)", "text": "closed"}],
          "valueMaps": [{"op": "=", "text": "open", "value": "1"}, {"op": "=", "text": "closed", "value": "0"},],
        })
    elif dtype == 'busy':
        ret.update({
          "colorMaps": [{"color": "rgb(183, 204, 102)", "text": "busy"}, {"color": "rgb(65, 82, 0)", "text": "idle"}],
          "valueMaps": [{"op": "=", "text": "busy", "value": "1"}, {"op": "=", "text": "idle", "value": "0"},],
        })
    elif dtype == 'on':
        ret.update({
          "colorMaps": [{"color": "rgb(144, 72, 138)", "text": "on"}, {"color": "rgb(58, 0, 53)", "text": "off"}],
          "valueMaps": [{"op": "=", "text": "on", "value": "1"}, {"op": "=", "text": "off", "value": "0"},],
        })
    elif dtype == 'motion':
        ret.update({
          "colorMaps": [{"color": "rgb(72, 111, 136)", "text": "motion"}, {"color": "rgb(3, 34, 54)", "text": "no"}],
          "valueMaps": [{"op": "=", "text": "motion", "value": "1"}, {"op": "=", "text": "no", "value": "0"},],
        })
        
    else: raise NotImplementedError()
        
    return ret
    
    
root = '/opt/grafana/dashboards'
def clearDir():
    for p in os.listdir(root):
        os.unlink(root + '/' + p)
    
def writeDashboard(title, rows, timeSpan='3h'):
    with open('%s/%s.json' % (root, title.replace(' ', '_')), 'w') as out:    
        out.write(json.dumps({
            "__inputs": [
                {"name": "DS_TELEGRAF", "label": "telegraf", "description": "", "type": "datasource", "pluginId": "influxdb", "pluginName": "InfluxDB"}
            ],
            "__requires": [
                {"type": "grafana", "id": "grafana", "name": "Grafana", "version": "4.4.3"},
                {"type": "panel", "id": "graph", "name": "Graph", "version": ""},
                {"type": "datasource", "id": "influxdb", "name": "InfluxDB", "version": "1.0.0"}
            ],
            "editable": true,
            "id": nextId(),
            "schemaVersion": 14,
            "rows": rows,
            "annotations": {"list": []},
            "tags": [],
            "time": {"from": "now-%s" % timeSpan, "to": "now"},
            "timepicker": {
                "refresh_intervals": ["5s", "10s", "30s", "1m", "5m", "15m", "30m", "1h", "2h", "1d"],
                "time_options": ["5m", "15m", "1h", "6h", "12h", "24h", "2d", "7d", "30d"]
            },
            "title": title,
        }))

clearDir()
writeDashboard('pi cpu', [
    {"height": 250, "panels": [cpu_usage_panel(process_name='piNode', hosts=piNodes)],},
    {"height": 250, "panels": [cpu_usage_panel(process_name='arduinoNode', hosts=['bang'])],},
    {"height": 250, "panels": [cpu_usage_panel(process_name='rssiscan', hosts=piNodes + ['bang', 'dash'])],},
    {"height": 250, "panels": [cpu_usage_panel_targets('webcam', [metric(alias=alias, measurement="procstat", field="cpu_usage", tags=t) for alias, t in webcamTags])],},
    {"height": 250, "panels": [cpu_usage_panel(process_name='chromium', hosts=['frontdoor'])],},
])

writeDashboard('ping from bang', [
     {"height": 1000, "panels": [
         float_panel(datasource='telegraf', title='ping from bang (max ms)', max=50, targets=[
             metric(alias=h, measurement='ping', field='maximum_response_ms', avg=5, tags=[('host', 'bang'), ('url', h)])
             for h in pingHosts
         ]),
     ]}])

def audioPanel(title, loc):
    sel = {"type": "percentile", "params": ["90"]}
    return {
        "datasource": "main",
        "id": nextId(),
        "interval": ">10s",
        "span": 12,
        "targets": [
            {"alias": "lo",
             "dsType": "influxdb",
             "groupBy": [{"params": ["$__interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
             "measurement": "audioLevel",
             "select": [[{"params": ["lo"], "type": "field"}, sel]],
             "tags": [{"key": "location", "operator": "=", "value": loc}],
             "policy": "default",
             "resultFormat": "time_series",
             "orderByTime": "ASC",
             "refId": "A"
         },
            {"alias": "mid",
             "dsType": "influxdb",
             "groupBy": [{"params": ["$__interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
             "measurement": "audioLevel",
             "select": [[{"params": ["mid"], "type": "field"}, sel]],
             "tags": [{"key": "location", "operator": "=", "value": loc}],
             "policy": "default",
             "resultFormat": "time_series",
             "orderByTime": "ASC",
             "refId": "B"
         },
            {"alias": "hi",
             "dsType": "influxdb",
             "groupBy": [{"params": ["$__interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
             "measurement": "audioLevel",
             "select": [[{"params": ["hi"], "type": "field"}, sel]],
             "tags": [{"key": "location", "operator": "=", "value": loc}],
             "policy": "default",
             "resultFormat": "time_series",
             "orderByTime": "ASC",
             "refId": "C"
         }
        ],
        "title": title,
        "type": "graph",
        "yaxes": [{"format": "short", "max": "2.5", "min": 0, "show": true, "decimals": null}, {"format": "short", "min": 0, "show": true}],
        "renderer": "flot",
        "xaxis": {"show": true, "mode": "time", "name": null, "values": [], "buckets": null},
        "lines": true,
        "fill": 1,
        "linewidth": 2,
        "dashes": false,
        "dashLength": 10,
        "spaceLength": 10,
        "points": false,
        "pointradius": 5,
        "bars": false,
        "stack": false,
        "percentage": false,
        "legend": {"show": true, "values": false, "min": false, "max": false, "current": false, "total": false, "avg": false},
        "nullPointMode": "null",
        "steppedLine": false,
        "tooltip": {"value_type": "individual", "shared": true, "sort": 0},
        "timeFrom": null,
        "timeShift": null,
        "aliasColors": {},
        "seriesOverrides": [
            {"alias": "lo", "color": "#0a50a1"},
            {"alias": "mid", "color": "#5195ce"},
            {"alias": "hi", "color": "#64b0c8"}
        ],
  "thresholds": [],
        "links": []
    }
writeDashboard('audio level', [
    {"height": 250,
     "panels": [
         #float_panel(datasource='main', title=title, max=1,
         #            targets=[metric(alias='level', measurement='audioLevel',  field='value', tags=[('location', loc)])])
         audioPanel(title, loc)
     ],
 } for title, loc in audioHosts
])


writeDashboard('presence', [
    {'height': 30, 'panels': [discrete_panel('dash idle',                 dtype='busy', measurement='presence', tags=[('sensor', 'xidle'), ('host', 'dash')])]},
    {'height': 30, 'panels': [discrete_panel('slash idle',                dtype='busy', measurement='presence', tags=[('sensor', 'xidle'), ('host', 'slash')])]},
    {'height': 30, 'panels': [discrete_panel('front door open',           dtype='open', measurement='state',    tags=[('sensor', 'open'), ('location', "frontDoor")]),]},
] + [
    {'height': 30, 'panels': [discrete_panel('%s on wifi' % name,         dtype='on',   measurement='presence', tags=[('sensor', 'wifi'), ('address', addr)])]} for name, addr in wifis
] + [
    
    ])

writeDashboard('motion', [
    {'height': 30, 'panels': [discrete_panel("motion storage",            dtype='motion', measurement="presence", tags=[("location", "storage")])] },
    {'height': 30, 'panels': [discrete_panel("motion bed",                dtype='motion', measurement="presence", tags=[("location", "bed")])] },
    {'height': 30, 'panels': [discrete_panel("motion ari bed",            dtype='motion', measurement="presence", tags=[("location", "ariBed")])] },
    {'height': 30, 'panels': [discrete_panel("motion ari desk",           dtype='motion', measurement="presence", tags=[("location", "ariDesk")])] },
    {'height': 30, 'panels': [discrete_panel("motion changing",           dtype='motion', measurement="presence", tags=[("location", "changing")])] },
    {'height': 30, 'panels': [discrete_panel("motion garage door inside", dtype='motion', measurement="presence", tags=[("location", "garageDoorInside")])] },
    {'height': 30, 'panels': [discrete_panel("motion front door inside",  dtype='motion', measurement="presence", tags=[("location", "frontdoorInside")])] },
    
    ])



def stacked_percent_panel(title, tags, measurement, fields):
    return {
        "datasource": "telegraf",
        "fill": 1,
        "id": nextId(),
        "interval": "10s",
        "legend": {"avg": false, "current": false, "max": false, "min": false, "show": true, "total": false, "values": false},
        "lines": true,
        "linewidth": 1,
        "nullPointMode": "null",
        "renderer": "flot",
        "span": 12,
        "spaceLength": 10,
        "stack": true,
        "tooltip": {"shared": true, "sort": 0, "value_type": "individual"},
        "type": "graph",
        "targets": [
            {
              "dsType": "influxdb", "orderByTime": "ASC", "policy": "default", "refId": nextId(), "resultFormat": "time_series",
                "measurement": measurement, "alias": alias,
                "groupBy": [{"params": ["$__interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
                "select": [[{"params": [field], "type": "field"}, {"params": [], "type": "mean"}]],
                "tags": tagList(tags)
            } for field, alias in fields
        ],
          "title": title,
        "yaxes": [
            {"format": "percent", "min": 0, "show": true,
             "max": 101}, # to make top line display right
            {"show": false}
        ]
    }

def host_cpu_breakdown(host):
    return stacked_percent_panel(title='%s CPU' % host,
                                 tags=[('host', host)],
                                 measurement='cpu',
                                 fields=[('usage_%s' % f, f) for f in [
                                     #  https://github.com/influxdata/telegraf/blob/master/plugins/inputs/system/CPU_README.md#description
                                     'user', 'system',  'nice', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice','idle',
                                 ]])
    
writeDashboard('CPU', [
    {"height": "250px", "panels": [host_cpu_breakdown(host=h)]} for h in ['bang', 'dash', 'slash', 'prime']
    ])

def mem_panel(host):
    return  {
        "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false, "datasource": "telegraf", "fill": 1, "id": 1, "interval": ">10s",
        "legend": {"avg": false, "current": false, "max": false, "min": false, "show": true, "total": false, "values": false},
        "lines": true, "linewidth": 1, "nullPointMode": "null", "pointradius": 5, "points": false, "renderer": "flot", "spaceLength": 10, "span": 6, "stack": true,
        "targets": [
            {"dsType": "influxdb",
             "groupBy": [{"params": ["$__interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
             "measurement": "mem", "orderByTime": "ASC", "policy": "default", "refId": nextId(), "resultFormat": "time_series",
             "select": [[{"params": [f], "type": "field"}, {"params": [], "type": "mean"}]],
             "tags": [{"key": "host", "operator": "=", "value": host}]} for f in ['used', 'buffered', 'cached', 'free']
        ],
        "title": "%s ram" % host,
        "tooltip": {"shared": true, "sort": 0, "value_type": "individual"},
        "type": "graph",
        "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []},
        "yaxes": [{"format": "bytes", "label": null, "logBase": 1, "max": null, "min": "0", "show": true}, {"show": false}]}
    
def swap_panel(host):
    return {
        "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false,
        "datasource": "telegraf", "fill": 1, "id": 5,
        "legend": {"avg": false, "current": false, "max": false, "min": false, "show": false, "total": false, "values": false},
        "lines": true, "linewidth": 1, "nullPointMode": "null", "pointradius": 5, "points": false, "renderer": "flot", "spaceLength": 10, "span": 6, "stack": false, 
        "targets": [
            {"dsType": "influxdb",
             "groupBy": [{"params": ["$__interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
             "measurement": "swap", "orderByTime": "ASC", "policy": "default", "refId": "A", "resultFormat": "time_series",
             "select": [[{"params": ["used"], "type": "field"}, {"params": [], "type": "mean"}]],
             "tags": [{"key": "host", "operator": "=", "value": host}]}],
        "thresholds": [], "timeFrom": null, "timeShift": null, "title": "%s swap used" % host,
        "tooltip": {"shared": true, "sort": 0, "value_type": "individual"}, "type": "graph",
        "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []},
        "yaxes": [{"format": "bytes", "label": null, "logBase": 1, "max": null, "min": "0", "show": true}, {"show": false}]}

def process_mem_panel(host, process):
    tags = tagList([('host', host), ('process_name', process)])
    return {
        "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false, "datasource": "telegraf", "fill": 1, "id": nextId(),
        "legend": {"avg": false, "current": false, "max": false, "min": false, "show": true, "total": false, "values": false},
        "lines": true, "linewidth": 1, "nullPointMode": "null", "pointradius": 5, "points": false, "renderer": "flot",
        "spaceLength": 10, "span": 4, "stack": true, 
        "targets": [{"alias": "rss", "dsType": "influxdb",
                     "groupBy": [{"params": ["$__interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
                     "measurement": "procstat", "orderByTime": "ASC", "policy": "default", "refId": "A", "resultFormat": "time_series",
                     "select": [[{"params": ["memory_rss"], "type": "field"}, {"params": [], "type": "mean"}]],
                     "tags": tags},
                    {"alias": "swap", "dsType": "influxdb",
                     "groupBy": [{"params": ["$__interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
                     "measurement": "procstat", "orderByTime": "ASC", "policy": "default", "refId": "B", "resultFormat": "time_series",
                     "select": [[{"params": ["memory_swap"], "type": "field"}, {"params": [], "type": "mean"}]], 
                     "tags": tags}], 
        "title": process,
        "tooltip": {"shared": true, "sort": 0, "value_type": "individual"},
        "type": "graph", 
        "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []}, 
        "yaxes": [{"format": "bytes", "label": "", "logBase": 1, "max": "2000000000", "min": "0", "show": true}, {"show": false}]}
    
writeDashboard('bang mem', [
    {"height": 250, "panels": [mem_panel('bang'), swap_panel('bang')]},
    {"height": 250, "panels": [process_mem_panel(host='bang', process=p) for p in [
        "arduinoNode", "dropbox",  "influxdb", "mongod",  "netbars", "pimscreen", "reasoning", "ruler-analysis", "ruler-server", "sse_collector", "supervisord", "sync_dropbox.py", "wallscreen",]]},
        ])


writeDashboard('dash mem', [
    {"height": 250, "panels": [mem_panel('dash'), swap_panel('dash')]},
    {"height": 250, "panels": [process_mem_panel(host='dash', process=p) for p in []]},
        ])

def process_cpu_panel(host, process):
    return {
        "datasource": "telegraf",
        "editable": true,
        "fill": 1,
        "id": nextId(),
        "interval": "10s",
        "legend": {"show": true,},
        "lines": true,
        "linewidth": 1,
        "nullPointMode": "connected",
        "renderer": "flot",
        "spaceLength": 10,
        "span": 4,
        "stack": true,
        "targets": [
            {
                "alias": f,
                "dsType": "influxdb",
                "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["0"], "type": "fill"}],
                "measurement": "procstat",
                "orderByTime": "ASC",
                "policy": "default",
                "refId": nextId(),
                "resultFormat": "time_series",
                "select": [[{"params": ["cpu_time_%s" % f], "type": "field"}, {"params": [], "type": "mean"}, {"params": ["1s"], "type": "non_negative_derivative"}]],
                "tags": tagList([('host', host), ('process_name', p)]),
            } for f in ['nice', 'iowait', 'system', 'user',]
        ],
        "title": p,
        "tooltip": {"msResolution": true, "shared": true, "sort": 0, "value_type": "cumulative"},
        "type": "graph",
        "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []},
        "yaxes": [
            {"format": "percentunit", "label": "", "logBase": 1, "max": 1, "min": 0, "show": true},
            {"format": "short", "label": null, "logBase": 1, "max": null, "min": null, "show": true}
        ]
    }

writeDashboard('bang processes', [
    {"height": 250, "panels": [
        process_cpu_panel(host='bang', process=p) for p in [
            'arduinoNode', 'dropbox',  "influxdb", "mongod",  "netbars", "pimscreen",
            "reasoning", "ruler-analysis", "ruler-server", "sse_collector", "supervisord",
            "sync_dropbox.py", "wallscreen",]
    ]}])

def cam_panel(location):
    return {
          "aliasColors": {},
          "bars": false,
          "dashLength": 10,
          "dashes": false,
          "datasource": "main",
          "editable": true,
          "error": false,
          "fill": 1,
          "id": 1,
          "legend": {"avg": false, "current": false, "max": false, "min": false, "show": true, "total": false, "values": false},
          "lines": true,
          "linewidth": 1,
          "links": [],
          "nullPointMode": "null",
          "percentage": false,
          "pointradius": 5,
          "points": false,
          "renderer": "flot",
          
          "scopedVars": {"location": {"selected": false, "text": "ari", "value": "ari"}},
          "seriesOverrides": [],
          "spaceLength": 10,
          "span": 12,
        "stack": false,
        "steppedLine": false,
        "targets": [
            {
              "alias": freq, "dsType": "influxdb",
                "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
                "measurement": "motion",
                "orderByTime": "ASC",
                "policy": "default",
                "refId": "A",
                "resultFormat": "time_series",
                "select": [[{"params": [freq], "type": "field"}, {"params": [], "type": "mean"}]],
                "tags": [{"key": "location", "operator": "=", "value": location}]} for freq in ['avg', 'mids']
          ],
          "title": "%s camera motion" % location,
          "tooltip": {"msResolution": false, "shared": true, "sort": 0, "value_type": "individual"},
          "type": "graph",
          "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []},
          "yaxes": [{"format": "short", "label": null, "logBase": 1, "max": null, "min": "0", "show": true}, {"format": "short", "label": null, "logBase": 1, "max": null, "min": null, "show": true}
          ]
        }

    
writeDashboard('cameras', [
    {"height": 250, "panels": [cam_panel(location=loc)],} for loc in camLocs] + [
        {"height": 250, "panels": [
            {"columns": [],
             "datasource": "main",
             "editable": true,
             "error": false,
             "fontSize": "100%",
             "id": nextId(),
             "showHeader": true,
             "sort": {"col": 0, "desc": true},
             "span": 12,
             "styles": [{"dateFormat": "YYYY-MM-DD HH:mm:ss", "pattern": "Time", "type": "date"},
                        {"colorMode": null,
                         "colors": ["rgba(245, 54, 54, 0.9)",
                                    "rgba(237, 129, 40, 0.89)",
                                    "rgba(50, 172, 45, 0.97)"],
                         "decimals": 0,
                         "pattern": "/Bytes$/",
                         "type": "number",
                         "unit": "bytes"}],
             "targets": [{"dsType": "influxdb",
                          "groupBy": [{"params": ["name"], "type": "tag"},
                                      {"params": ["host"], "type": "tag"}],
                          "measurement": "service",
                          "orderByTime": "ASC",
                          "policy": "default",
                          "query": "SELECT * FROM \"service\" WHERE \"name\" = 'unicam' AND $timeFilter",
                          "rawQuery": false,
                          "refId": "A",
                          "resultFormat": "table",
                          "select": [[{"params": ["*"], "type": "field"}]],
                          "tags": [{"key": "name", "operator": "=", "value": "unicam"}]}],
             "timeFrom": "30s", 
             "title": "webcam service",
             "transform": "table",
             "type": "table"}],
         },
])

def zfsDatasetTargets():
    return [{
        "alias": p,
        "groupBy": [{ "params": ["$__interval"],"type": "time" },{ "params": ["null"],"type": "fill" }],
        "measurement": "used_bytes",
        "orderByTime": "ASC",
        "policy": "default",
        "refId": nextId(),
        "resultFormat": "time_series",
        "select": [[{ "params": ["value"],"type": "field" },{ "params": [],"type": "mean" }]],"tags": [{ "key": "dataset","operator": "=","value": "stor6"+p }]
    } for p in [
#'/my',
'/my/archive/ALL',
'/my/backup',
#'/my/backup/ffg',
'/my/backup/mongo',
#'/my/cvsroot',
#'/my/darcs',
#'/my/darcs2',
'/my/dl',
#'/my/doc',
'/my/home',
#'/my/irc',
'/my/log',
'/my/mail',
'/my/music',
'/my/music/projects',
'/my/pda',
'/my/pic',
'/my/pic/digicam',
'/my/pic/phonecam',
#'/my/post',
'/my/proj',
#'/my/rayz',
'/my/site',
#'/my/tv',
'/my/video',

    ]]

writeDashboard('disk-free-space', timeSpan='7d', rows=[
    {
      "height": "250px",
      "panels": [
        
        {
          "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false, "datasource": "telegraf", "editable": true, "error": false,
          "fill": 1,
               "gridPos": {
        "h": 7,
        "w": 6,
        "x": 0,
        "y": 0
      },
"id": 2, "legend": {"avg": false, "current": false, "max": false, "min": false, "show": false, "total": false, "values": false},
          "lines": true, "linewidth": 2, "links": [], "nullPointMode": "null", "percentage": false, "pointradius": 5, "points": false, "renderer": "flot", "seriesOverrides": [], "spaceLength": 10, "span": 3, "stack": false, "steppedLine": false,
          "targets": [
            {
              "dsType": "influxdb",
              "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
              "measurement": "disk", "orderByTime": "ASC", "policy": "default", "refId": "A", "resultFormat": "time_series",
              "select": [[{"params": ["free"], "type": "field"}, {"params": [], "type": "mean"}]],
              "tags": [
                {"key": "host", "operator": "=", "value": "bang"},
                {"condition": "AND", "key": "path", "operator": "=", "value": "/"}
              ]
            }
          ],
          "thresholds": [],
          "timeFrom": null,
          "timeShift": null,
          "title": "bang root",
          "tooltip": {"msResolution": true, "shared": true, "sort": 0, "value_type": "cumulative"},
          "type": "graph",
          "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []},
          "yaxes": [
            {"format": "bytes", "label": null, "logBase": 1, "max": null, "min": 0, "show": true},
            {"format": "short", "label": null, "logBase": 1, "max": null, "min": null, "show": true}
          ]
        },
        {
          "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false, "datasource": "telegraf", "editable": true, "error": false,
          "fill": 1,  "gridPos": {
        "h": 7,
        "w": 6,
        "x": 6,
        "y": 0
      },"id": 5, "legend": {"avg": false, "current": false, "max": false, "min": false, "show": false, "total": false, "values": false},
          "lines": true, "linewidth": 2, "links": [], "nullPointMode": "null", "percentage": false, "pointradius": 5, "points": false, "renderer": "flot", "seriesOverrides": [], "spaceLength": 10, "span": 3, "stack": false, "steppedLine": false,
          "targets": [
            {
              "dsType": "influxdb",
              "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
              "measurement": "disk", "orderByTime": "ASC", "policy": "default", "refId": "A", "resultFormat": "time_series",
              "select": [[{"params": ["free"], "type": "field"}, {"params": [], "type": "mean"}]],
              "tags": [
                {"key": "host", "operator": "=", "value": "dash"},
                {"condition": "AND", "key": "path", "operator": "=", "value": "/"}
              ]
            }
          ],
          "thresholds": [],
          "timeFrom": null,
          "timeShift": null,
          "title": "dash root",
          "tooltip": {"msResolution": true, "shared": true, "sort": 0, "value_type": "cumulative"},
          "type": "graph",
          "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []},
          "yaxes": [
            {"format": "bytes", "label": null, "logBase": 1, "max": null, "min": 0, "show": true},
            {"format": "short", "label": null, "logBase": 1, "max": null, "min": null, "show": true}
          ]
        },
        {
          "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false, "datasource": "telegraf", "editable": true, "error": false,
          "fill": 1,    "gridPos": {
        "h": 7,
        "w": 6,
        "x": 12,
        "y": 0
      },"id": 6, "legend": {"avg": false, "current": false, "max": false, "min": false, "show": false, "total": false, "values": false},
          "lines": true, "linewidth": 2, "links": [], "nullPointMode": "null", "percentage": false, "pointradius": 5, "points": false, "renderer": "flot", "seriesOverrides": [], "spaceLength": 10, "span": 3, "stack": false, "steppedLine": false,
          "targets": [
            {
              "dsType": "influxdb",
              "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
              "measurement": "disk", "orderByTime": "ASC", "policy": "default", "refId": "A", "resultFormat": "time_series",
              "select": [[{"params": ["free"], "type": "field"}, {"params": [], "type": "mean"}]],
              "tags": [
                {"key": "host", "operator": "=", "value": "slash"},
                {"condition": "AND", "key": "path", "operator": "=", "value": "/"}
              ]
            }
          ],
          "thresholds": [],
          "timeFrom": null,
          "timeShift": null,
          "title": "slash root",
          "tooltip": {"msResolution": true, "shared": true, "sort": 0, "value_type": "cumulative"},
          "type": "graph",
          "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []},
          "yaxes": [
            {"format": "bytes", "label": null, "logBase": 1, "max": null, "min": 0, "show": true},
            {"format": "short", "label": null, "logBase": 1, "max": null, "min": null, "show": true}
          ]
        },
          {
              "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false, "datasource": "main", "fill": 1,
              "gridPos": { "h": 20,"w": 24,"x": 0,"y": 7 },
              "id": nextId(),  "interval": "10m",
              "legend": {"alignAsTable": true, "avg": false, "current": true, "hideZero": false, "max": false, "min": false, "rightSide": true, "show": true, "total": false, "values": true},
              "lines": true, "linewidth": 1, "links": [], "nullPointMode": "null", "percentage": false, "pointradius": 5, "points": false, "renderer": "flot",
              "seriesOverrides": [], "spaceLength": 10, "stack": true, "steppedLine": false,
              "targets": list(reversed([
                  {
                      "alias": "free",
                      "groupBy": [{ "params": ["$__interval"],"type": "time" },{ "params": ["null"],"type": "fill" }],
                      "measurement": "available_bytes",
                      "orderByTime": "ASC",
                      "policy": "default",
                      "refId": "A",
                      "resultFormat": "time_series",
                      "select": [[{ "params": ["value"],"type": "field" },{ "params": [],"type": "mean" }]],"tags": [{ "key": "volume","operator": "=","value": "stor6" }]
                  },
              ] + zfsDatasetTargets())),
              "thresholds": [],
              "timeFrom": null,
              "timeRegions": [],
              "timeShift": null,
              "title": "zfs stor6",
              "tooltip": { "shared": true,"sort": 0,"value_type": "individual" },
              "type": "graph",
              "xaxis": { "buckets": null,"mode": "time","name": null,"show": true,"values": [] },
              "yaxes": [
                  { "format": "bytes","label": null,"logBase": 1,"max": null,"min": "0","show": true },
                  { "format": "short","label": null,"logBase": 1,"max": null,"min": null,"show": true }
              ],
              "yaxis": { "align": false,"alignLevel": null }
          }
          
      ],
     
    },
])

writeDashboard('mongodb', timeSpan='1d', rows=[
    {
      "height": "250px",
      "panels": [
        {
            "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false, "datasource": "telegraf", "fill": 1, "id": nextId(),
            "legend": {"avg": false, "current": false, "max": false, "min": false, "show": true, "total": false, "values": false},
            "lines": true, "linewidth": 1, "links": [], "nullPointMode": "null", "percentage": false, "pointradius": 5, "points": false, "renderer": "flot", "repeat": "db",
            "scopedVars": {"db": {"selected": false, "text": db, "value": db}},
          "seriesOverrides": [{"alias": "objects", "yaxis": 2}],
          "spaceLength": 10,
          "span": 4,
          "stack": false,
          "steppedLine": false,
          "targets": [
            {
              "alias": "storage",
              "dsType": "influxdb",
              "groupBy": [{"params": ["$__interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
              "measurement": "mongodb_db_stats",
              "orderByTime": "ASC",
              "policy": "default",
              "refId": "A",
              "resultFormat": "time_series",
              "select": [[{"params": ["storage_size"], "type": "field"}, {"params": [], "type": "mean"}]],
              "tags": [{"key": "db_name", "operator": "=", "value": db}]
            },
            {
              "alias": "objects",
              "dsType": "influxdb",
              "groupBy": [{"params": ["$__interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
              "measurement": "mongodb_db_stats",
              "orderByTime": "ASC",
              "policy": "default",
              "refId": "B",
              "resultFormat": "time_series",
              "select": [[{"params": ["objects"], "type": "field"}, {"params": [], "type": "mean"}]],
              "tags": [{"key": "db_name", "operator": "=", "value": db}]
            }
          ],
          "thresholds": [], "timeFrom": null, "timeShift": null,
          "title": db,
          "tooltip": {"shared": true, "sort": 0, "value_type": "individual"},
          "type": "graph",
          "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []},
          "yaxes": [{"format": "bytes", "label": null, "logBase": 1, "max": null, "min": "0", "show": true}, {"format": "short", "label": null, "logBase": 1, "max": null, "min": null, "show": true}]} for db in mongoDbs
  ]}])

writeDashboard('power-usage', [
    {
        "height": "500px",
        "panels": [
            {
                "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false, "datasource": "main", "editable": true, "error": false, "fill": 1, "grid": {}, "id": 1, "interval": "8s", "legend": {"avg": false, "current": false, "max": false, "min": false, "show": false, "total": false, "values": false}, "lines": true, "linewidth": 1, "links": [], "nullPointMode": "null", "percentage": false, "pointradius": 5, "points": false, "renderer": "flot", "seriesOverrides": [], "spaceLength": 10, "span": 12, "stack": false, "steppedLine": false, "targets": [{"dsType": "influxdb", "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["null"], "type": "fill"}], "measurement": "housePowerW", "orderByTime": "ASC", "policy": "default", "refId": "A", "resultFormat": "time_series", "select": [[{"params": ["value"], "type": "field"}, {"params": [], "type": "mean"}]], "tags": [{"key": "house", "operator": "=", "value": "berkeley"}]}], "thresholds": [], "timeFrom": null, "timeShift": null, "title": "house power usage", "tooltip": {"msResolution": true, "shared": true, "sort": 0, "value_type": "cumulative"}, "type": "graph", "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []}, "yaxes": [{"format": "watt", "label": null, "logBase": 1, "max": null, "min": 0, "show": true}, {"format": "short", "label": null, "logBase": 1, "max": null, "min": null, "show": true}]
            },
            {
                "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false, "datasource": "main", "editable": true, "error": false, "fill": 1, "grid": {}, "id": 2, "legend": {"avg": false, "current": false, "max": false, "min": false, "show": true, "total": false, "values": false}, "lines": true, "linewidth": 2, "nullPointMode": "connected", "percentage": false, "pointradius": 5, "points": false, "renderer": "flot", "seriesOverrides": [], "spaceLength": 10, "span": 12, "stack": false, "steppedLine": false, "targets": [
                    {"dsType": "influxdb", "groupBy": [{"params": ["$interval"], "type": "time"}], "measurement": "housePowerSumDeliveredKwh", "policy": "default", "refId": "B", "resultFormat": "time_series", "select": [[{"params": ["value"], "type": "field"}, {"params": [], "type": "max"}, {"params": ["1h"], "type": "derivative"}]], "tags": [{"key": "house", "operator": "=", "value": "berkeley"}]}], "thresholds": [], "timeFrom": null, "timeShift": null, "title": "Panel Title", "tooltip": {"msResolution": true, "shared": true, "sort": 0, "value_type": "cumulative"}, "type": "graph", "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []}, "yaxes": [{"format": "short", "label": null, "logBase": 1, "max": null, "min": null, "show": true}, {"format": "short", "label": null, "logBase": 1, "max": null, "min": null, "show": true}]
            },
            {
                "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false, "datasource": "main", "editable": true, "error": false, "fill": 1, "grid": {}, "id": 3, "legend": {"alignAsTable": false, "avg": false, "current": false, "max": false, "min": false, "rightSide": false, "show": false, "total": false, "values": false}, "lines": true, "linewidth": 2, "links": [], "nullPointMode": "connected", "percentage": false, "pointradius": 5, "points": false, "renderer": "flot", "seriesOverrides": [], "spaceLength": 10, "span": 12, "stack": false, "steppedLine": false, "targets": [{"dsType": "influxdb", "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["null"], "type": "fill"}], "measurement": "housePowerW", "policy": "default", "refId": "A", "resultFormat": "table", "select": [[{"params": ["value"], "type": "field"}, {"params": [], "type": "integral"}]], "tags": [{"key": "house", "operator": "=", "value": "berkeley"}]}], "thresholds": [], "timeFrom": null, "timeShift": null, "title": "house power usage", "tooltip": {"msResolution": true, "shared": true, "sort": 0, "value_type": "cumulative"}, "type": "graph", "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []}, "yaxes": [{"format": "watth", "label": null, "logBase": 1, "max": null, "min": 0, "show": true}, {"format": "short", "label": null, "logBase": 1, "max": null, "min": null, "show": true}]
            }
        ],
        
    }
  ]
 )

writeDashboard('ruler', timeSpan='7d', rows=[
    {
      "height": "600px",
      "panels": [
        {
          "aliasColors": {},
          "bars": false,
          "dashLength": 10,
          "dashes": false,
          "datasource": "main",
          "editable": true,
          "error": false,
          "fill": 1,
          "grid": {},
          "id": 1,
          "legend": {"avg": false, "current": false, "max": false, "min": false, "show": true, "total": false, "values": false},
          "lines": true,
          "linewidth": 2,
          "links": [],
          "nullPointMode": "connected",
          "percentage": false,
          "pointradius": 5,
          "points": false,
          "renderer": "flot",
          "seriesOverrides": [],
          "spaceLength": 10,
          "span": 12,
          "stack": false,
          "steppedLine": false,
          "targets": [
            {
              "alias": "total",
              "dsType": "influxdb",
              "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
              "measurement": "ruler",
              "policy": "default",
              "refId": "A",
              "resultFormat": "time_series",
              "select": [[{"params": ["value"], "type": "field"}, {"params": [], "type": "mean"}]],
              "tags": [{"key": "state", "operator": "=", "value": "total"}]
            },
            {
              "alias": "failing",
              "dsType": "influxdb",
              "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
              "measurement": "ruler",
              "policy": "default",
              "refId": "B",
              "resultFormat": "time_series",
              "select": [[{"params": ["value"], "type": "field"}, {"params": [], "type": "mean"}]],
              "tags": [{"key": "state", "operator": "=", "value": "failing"}]
            }
          ],
          "thresholds": [],
          "timeFrom": null,
          "timeShift": null,
          "title": "ruler checks",
          "tooltip": {"msResolution": true, "shared": true, "sort": 0, "value_type": "cumulative"},
          "type": "graph",
          "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []},
          "yaxes": [{"format": "short", "label": "count", "logBase": 1, "max": null, "min": 0, "show": true}, {"format": "short", "label": null, "logBase": 1, "max": null, "min": null, "show": true}]
        }
      ],
      
     
    },
    {
      "height": 261,
      "panels": [
        {
          "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false, "datasource": "telegraf", "editable": true, "error": false, "fill": 1, "grid": {}, "id": 2, "legend": {"avg": false, "current": false, "max": false, "min": false, "show": true, "total": false, "values": false},
          "lines": true, "linewidth": 2, "links": [], "nullPointMode": "connected", "percentage": false, "pointradius": 5, "points": false, "renderer": "flot", "seriesOverrides": [], "spaceLength": 10, "span": 12, "stack": false, "steppedLine": false,
          "targets": [
            {
                "alias": "RSS", "dsType": "influxdb",
                "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["null"], "type": "fill"}], "measurement": "procstat", "orderByTime": "ASC", "policy": "default", "refId": "A", "resultFormat": "time_series",
                "select": [[{"params": ["memory_rss"], "type": "field"}, {"params": [], "type": "mean"}]],
                "tags": [{"key": "host", "operator": "=", "value": "bang"}, {"condition": "AND", "key": "process_name", "operator": "=", "value": "ruler-server"}]
            },
            {
              "alias": "VM", "dsType": "influxdb",
                "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["null"], "type": "fill"}], "measurement": "procstat", "orderByTime": "ASC", "policy": "default", "refId": "C", "resultFormat": "time_series",
                "select": [[{"params": ["memory_vms"], "type": "field"}, {"params": [], "type": "mean"}]],
                "tags": [{"key": "host", "operator": "=", "value": "bang"}, {"condition": "AND", "key": "process_name", "operator": "=", "value": "ruler-server"}]
            }
          ],
          "thresholds": [],
          "timeFrom": null,
          "timeShift": null,
          "title": "ruler-server mem",
          "tooltip": {"msResolution": true, "shared": true, "sort": 0, "value_type": "cumulative"},
          "type": "graph",
          "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []},
            "yaxes": [{"format": "bytes", "label": null, "logBase": 1, "max": null, "min": null, "show": true}, {"format": "bytes", "label": null, "logBase": 1, "max": null, "min": null, "show": false}]
        }
      ],
      
   
    },
    {
      "height": 255,
      "panels": [
        {
          "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false, "datasource": "telegraf", "editable": true, "error": false, "fill": 1, "grid": {}, "id": 4, "legend": {"avg": false, "current": false, "max": false, "min": false, "show": true, "total": false, "values": false},
          "lines": true, "linewidth": 2, "links": [], "nullPointMode": "connected", "percentage": false, "pointradius": 5, "points": false, "renderer": "flot", "seriesOverrides": [], "spaceLength": 10, "span": 12, "stack": false, "steppedLine": false,
          "targets": [
            {
              "alias": "RSS",
              "dsType": "influxdb",
              "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
              "measurement": "procstat",
              "orderByTime": "ASC",
              "policy": "default",
              "refId": "A",
              "resultFormat": "time_series",
              "select": [ [ { "params": [ "memory_rss" ], "type": "field" }, { "params": [], "type": "mean" } ] ],
              "tags": [ { "key": "host", "operator": "=", "value": "bang" }, { "condition": "AND", "key": "process_name", "operator": "=", "value": "ruler-analysis" } ]
            },
            {
              "alias": "VM",
              "dsType": "influxdb",
              "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
              "measurement": "procstat",
              "orderByTime": "ASC",
              "policy": "default",
              "refId": "C",
              "resultFormat": "time_series",
              "select": [ [ { "params": [ "memory_vms" ], "type": "field" }, { "params": [], "type": "mean" } ] ],
              "tags": [ { "key": "host", "operator": "=", "value": "bang" }, { "condition": "AND", "key": "process_name", "operator": "=", "value": "ruler-analysis" } ]
            }
          ],
          "thresholds": [],
          "timeFrom": null,
          "timeShift": null,
          "title": "ruler-analysis mem",
          "tooltip": {"msResolution": true, "shared": true, "sort": 0, "value_type": "cumulative"},
          "type": "graph",
          "xaxis": { "buckets": null, "mode": "time", "name": null, "show": true, "values": [] },
            "yaxes": [ { "format": "bytes", "label": null, "logBase": 1, "max": null, "min": null, "show": true }, { "format": "bytes", "label": null, "logBase": 1, "max": null, "min": null, "show": false } ]
        }
      ],
      
    
    },
  
  
    ])


def tempTarget(location, measurement='temperatureF'):
    return {
              "alias": location,
              "dsType": "influxdb",
              "fill": "",
              "groupBy": [{"params": ["$interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
              "measurement": measurement,
              "orderByTime": "ASC",
              "policy": "default",
              "query": "SELECT mean(\"value\") AS \"value\" FROM \"%s\" WHERE \"location\" = '%s' AND $timeFilter GROUP BY time(undefined), \"undefined\"" % (measurement, location),
              "refId": nextId(),
              "resultFormat": "time_series",
              "select": [[{"params": ["value"], "type": "field"}, {"params": [], "type": "median"}]],
              "tags": [{"key": "location", "operator": "=", "value": location}]
            }
    

def tempRow(title, targets, yFormat='farenheit', yMin=40, yMax=110):
    return {"height": "450px", "panels": [{
        "aliasColors": {}, "bars": false, "dashLength": 10, "dashes": false, "datasource": "main", "editable": true, "error": false, "fill": 1,
        "grid": {"leftLogBase": 1, "leftMax": null, "leftMin": null, "rightLogBase": 1, "rightMax": null, "rightMin": null},
        "id": nextId(),
        "legend": {"avg": false, "current": false, "max": false, "min": false, "show": true, "total": false, "values": false},
        "lines": true, "linewidth": 2, "links": [], "nullPointMode": "connected",
        "percentage": false, "pointradius": 5, "points": false, "renderer": "flot", "seriesOverrides": [], "spaceLength": 10, "span": 12, "stack": false, "steppedLine": false,
        "targets": targets,
        "thresholds": [], "timeFrom": null, "timeShift": null,
        "title": title,
        "tooltip": {"msResolution": true, "shared": true, "sort": 2, "value_type": "cumulative"},
        "type": "graph",
        "x-axis": true,
        "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []},
        "y-axis": true,
        "y_formats": ["short", "short"],
        "yaxes": [
            {"format": yFormat, "label": "", "logBase": 1, "max": yMax, "min": yMin, "show": true},
            {"format": "short", "label": null, "logBase": 1, "max": null, "min": null, "show": true}
        ]
        }],  }
     

writeDashboard('temperatures', timeSpan='1d', rows=[

          tempRow(title="house temperatures", targets=[
            tempTarget("greenhouse"),
            tempTarget("storage"),
            tempTarget("frontbedUnderDesk"),
            tempTarget("workshop"),
            tempTarget("printer-low"),
            tempTarget("printer-mid"),
            tempTarget("printer-high"),
            tempTarget("garage"),
            tempTarget("bedroom"),
            tempTarget("livingRoomCeiling"),
            tempTarget("kitchenCounter"),
          ]),
          tempRow(title="humidity", targets=[
              tempTarget('greenhouse', 'humidity'),
              tempTarget('livingRoomCeiling', 'humidity'),
              tempTarget('kitchenCounter', 'humidity'),
              tempTarget('workshop', 'humidity'),
          ], yFormat='short', yMin=0, yMax=100),
          tempRow(title='NOAA', targets= [
              tempTarget('koak'),
              tempTarget('kmhr'),
              tempTarget('kont'),
              tempTarget('ksfo'),
          ]),
          tempRow(title="Pi board temperatures", targets=[
              tempTarget('changingPi'),
              tempTarget('bedPi'),
              tempTarget('kitchenPi'),
              tempTarget('livingPi'),
              tempTarget('garagePi'),
              tempTarget('frontDoor'),
              tempTarget('frontbed'),
          ]),
          tempRow(title="bang sensors", targets=[
            {
                "alias": c,
                "dsType": "influxdb", "groupBy": [{"params": ["$__interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
                "measurement": "sensors", "orderByTime": "ASC", "policy": "default", "refId": nextId(),
                "resultFormat": "time_series",
                "select": [[{"params": ["temp_input"], "type": "field"}, {"params": [], "type": "mean"}]],
                "tags": [{"key": "host", "operator": "=", "value": "bang"}, {"condition": "AND", "key": "feature", "operator": "=", "value": c}]
            } for c in ['core_0', 'core_1', 'core_2', 'core_3', 'temp1']
          ], yFormat='celsius', yMin=26, yMax=60),
    ])

def netRow(host):
    return { "dashLength": 10, "dashes": false, "datasource": "telegraf", "fill": 1, "id": nextId(), "interval": ">10s", 
             "legend": { "show": true},
             "lines": true, "linewidth": 1, "links": [], "nullPointMode": "null", "percentage": false, "pointradius": 5, "points": false,
             "renderer": "flot", "seriesOverrides": [], "spaceLength": 10, "span": 4, "stack": false, "steppedLine": false, 
             "targets": [{
                 "alias": "recv",
                 "dsType": "influxdb",
                 "groupBy": [{"params": ["$__interval"], "type": "time"}, {"params": ["null"], "type": "fill"}],
                 "measurement": "net", "orderByTime": "ASC", "policy": "default", "refId": "A",
                 "resultFormat": "time_series", 
                 "select": [[{"params": ["bytes_recv"], "type": "field"},
                             {"params": [], "type": "mean"},
                             {"params": ["1s"], "type": "non_negative_derivative"}]], 
                 "tags": [{"key": "host", "operator": "=", "value": host}]},
                         {"alias": "sent", "dsType": "influxdb",
                          "groupBy": [{"params": ["$__interval"], "type": "time"},
                                      {"params": ["null"], "type": "fill"}],
                          "measurement": "net", "orderByTime": "ASC", "policy": "default",
                          "refId": "B", "resultFormat": "time_series", 
                          "select": [[{"params": ["bytes_sent"], "type": "field"},
                                      {"params": [], "type": "mean"}, {"params": ["1s"], "type": "non_negative_derivative"}]], 
                          "tags": [{"key": "host", "operator": "=", "value": host}]}], 
             "thresholds": [], "timeFrom": null, "timeShift": null,
             "title": "%s net" % host,
             "tooltip": {"shared": true, "sort": 0, "value_type": "individual"},
             "type": "graph", 
             "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []}, 
             "yaxes": [{"format": "bytes", "min": "0", "max":500000, "show": true},
                       {"format": "short", "show": true}]}
    

writeDashboard('network', timeSpan='1d', rows=[
    {"height": "450px", "panels": [
        { "dashLength": 10, "dashes": false, "datasource": "main", "editable": true, "error": false, "fill": 1, "grid": {}, "id": 1, 
          "legend": { "show": false}, "lines": true, "linewidth": 2, "links": [], "nullPointMode": "connected", "percentage": false, "pointradius": 5, "points": false,
          "renderer": "flot", "seriesOverrides": [], "spaceLength": 10, "span": 12, "stack": false, "steppedLine": false, 
          "targets": [{
              "alias": "in", "dsType": "influxdb",
              "groupBy": [{"params": ["$interval"], "type": "time"},
                          {"params": ["null"], "type": "fill"}],
              "measurement": "bytesPerSec", "policy": "default",
              "query": "SELECT moving_average(mean(\"value\"), 10)  * -1 FROM \"bytesPerSec\" WHERE \"source\" = 'isp' AND $timeFilter GROUP BY time($interval) fill(null)",
              "rawQuery": false,
              "refId": "B",
              "resultFormat": "time_series", 
              "select": [[{"params": ["value"], "type": "field"},
                          {"params": [], "type": "max"}]], 
              "tags": [{"key": "source", "operator": "=", "value": "isp"}]}], 
          "thresholds": [], "timeFrom": null, "timeShift": null,
          "title": "in from ISP",
          "tooltip": {"msResolution": true, "shared": true, "sort": 0, "value_type": "cumulative"},
          "type": "graph", 
          "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []}, 
          "yaxes": [{"format": "Bps", "label": "", "logBase": 1, "max": 1500000, "min": 0, "show": true}, {"format": "short", "show": true}]
      },
        { "dashLength": 10, "dashes": false, "datasource": "main", "editable": true, "error": false, "fill": 1, "grid": {}, "id": nextId(), 
          "legend": { "show": false}, "lines": true, "linewidth": 2, "links": [], "nullPointMode": "connected", "percentage": false, "pointradius": 5, "points": false,
          "renderer": "flot", "seriesOverrides": [], "spaceLength": 10, "span": 12, "stack": false, "steppedLine": false, 
          "targets": [{
              "alias": "out", "dsType": "influxdb", "groupBy": [{"params": ["$interval"], "type": "time"},
                                                                {"params": ["null"], "type": "fill"}], "measurement": "bytesPerSec", "policy": "default", "refId": nextId(), "resultFormat": "time_series", 
              "select": [[{"params": ["value"], "type": "field"}, {"params": [], "type": "max"}]], 
              "tags": [{"key": "source", "operator": "=", "value": "bang"}]}], 
          "thresholds": [], "timeFrom": null, "timeShift": null,
          "title": "out to ISP", "tooltip": {"msResolution": true, "shared": true, "sort": 0, "value_type": "cumulative"}, "type": "graph", 
          "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []}, 
          "yaxes": [{"format": "Bps", "label": null, "logBase": 1, "max": 210000, "min": 0, "show": true},
                    {"format": "short", "show": true}]
      }]},
    {"height": 250, "panels": [
        { "dashLength": 10, "dashes": false, "datasource": "telegraf", "fill": 1, "id": 3, 
          "legend": { "show": true}, "lines": true, "linewidth": 1, "links": [], "nullPointMode": "null", "percentage": false, "pointradius": 5, "points": false,
          "renderer": "flot", "seriesOverrides": [], "spaceLength": 10, "span": 12, "stack": false, "steppedLine": false, 
          "targets": [{"dsType": "influxdb", "groupBy": [
              {"params": ["$__interval"], "type": "time"},
              {"params": ["null"], "type": "fill"}
          ], "measurement": "procstat", "orderByTime": "ASC", "policy": "default", "refId": nextId(), "resultFormat": "time_series", 
                       "select": [[{"params": ["cpu_usage"], "type": "field"}, {"params": [], "type": "mean"}]], 
                       "tags": [{"key": "process_name", "operator": "=", "value": "netbars"}]}], 
          "thresholds": [], "timeFrom": null, "timeShift": null,
          "title": "netbars cpu usage", "tooltip": {"shared": true, "sort": 0, "value_type": "individual"}, "type": "graph", 
          "xaxis": {"buckets": null, "mode": "time", "name": null, "show": true, "values": []}, 
          "yaxes": [{"format": "short", "show": true}, {"format": "short", "show": true}]}
    ],  },
    
    {"height": 239, "panels": [
        netRow('changing'),
        netRow('slash'),
        netRow('bed'),
        netRow('dash'),
        netRow('garage'),
        netRow('frontdoor'),
        netRow('kitchen'),
        netRow('living'),
    ]}])
