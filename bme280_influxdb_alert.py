'''
influxdbからデータを取得して異常値だったらslackに通知する


'''
import sys, os, re
import time
import json
import urllib.request

import argparse

from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import ASYNCHRONOUS

SCRIPT_NAME = os.path.basename(__file__)

INFLUX_HOST = "http://{}:8086"
INFLUX_TOKEN = ""
INFLUX_ORG = "pydev"
INFLUX_BUCKET = ""
MEASUREMENT = "bme280"
INFLUX_CLIENT = None
SENSOR_CLIENT = "rp006"

INFLUX_QUERY = 'from(bucket: "{0}") \
    |> range(start: -1m) \
    |> filter(fn: (r) => r["_measurement"] == "{1}") \
    |> filter(fn: (r) => r["_field"] == "temperature") \
    |> filter(fn: (r) => r["hostname"] == "{2}") \
    |> aggregateWindow(every: 10s, fn: mean, createEmpty: false) \
    |> yield(name: "mean")'

WEB_HOOK = ""


'''
Slackへpostする関数

'''
def post_slack(title, msg, color):
    post_fields = [{
        "title": title,
        "value": msg,
        "short": False
    }]

    post_data = {
        'attachments':  [{
            'color': color,
            'fields': post_fields
        }]
    }

    method = 'POST'
    request_headers = { 'Content-Type': 'application/json; charset=utf-8' }
    body = json.dumps(post_data).encode("utf-8")
    request = urllib.request.Request(
        url=WEB_HOOK, 
        data=body, 
        method=method,
        headers=request_headers 
    )
    urllib.request.urlopen(request)
    return


# メイン関数   この関数は末尾のif文から呼び出される
def main():
    # データの取得
    # ref https://github.com/influxdata/influxdb-client-python
    tables = INFLUX_CLIENT.query_api().query(INFLUX_QUERY)
    _last_value = tables[0].records[-1].values["_value"]

    print(_last_value)

    if _last_value > 40.0:
        title = '障害通知'
        msg = '{} の温度が{:.2f}です。'.format(SENSOR_CLIENT, _last_value)
        color = 'danger'
        post_slack(title, msg, color)
    elif _last_value > 35.0:
        title = '警告'
        msg = '{} の温度が{:.2f}です。'.format(SENSOR_CLIENT, _last_value)
        color = 'warning'
        post_slack(title, msg, color)

    time.sleep(10)


if __name__ == '__main__':          # importされないときだけmain()を呼ぶ
    parser = argparse.ArgumentParser()
    parser.add_argument("--infhost", type=str, default="localhost", help="hostname or ip")
    parser.add_argument("--inftoken", type=str, default="", help="token to write db")
    parser.add_argument("--infbucket", type=str, default="", help="bucketname")
    parser.add_argument("--sensorclient", type=str, default="", help="hostname of raspberrypi")
    parser.add_argument("--webhookuri", type=str, default="", help="webhook")
    
    args = parser.parse_args()
    INFLUX_HOST = INFLUX_HOST.format(args.infhost)
    INFLUX_TOKEN = args.inftoken
    INFLUX_BUCKET = args.infbucket
    SENSOR_CLIENT = args.sensorclient
    INFLUX_QUERY = INFLUX_QUERY.format(INFLUX_BUCKET, MEASUREMENT, SENSOR_CLIENT)
    INFLUX_CLIENT = InfluxDBClient(url=INFLUX_HOST, token=INFLUX_TOKEN, org=INFLUX_ORG)
    WEB_HOOK = args.webhookuri
    
    while True:
        main()    # メイン関数を呼び出す
