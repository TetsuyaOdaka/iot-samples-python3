'''
influxdbからデータを取得する


'''
import sys, os, re
import time
import json

import argparse

from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import ASYNCHRONOUS

SCRIPT_NAME = os.path.basename(__file__)

INFLUX_HOST = "http://{}:8086"
INFLUX_TOKEN = ""
INFLUX_ORG = "pydev"
INFLUX_BUCKET = ""
MEASUREMENT = "bme280"
FLUX_CLIENT = None
SENSOR_CLIENT = "rp006"

INFLUX_QUERY = 'from(bucket: "{0}") \
    |> range(start: -1m) \
    |> filter(fn: (r) => r["_measurement"] == "{1}") \
    |> filter(fn: (r) => r["_field"] == "temperature") \
    |> filter(fn: (r) => r["hostname"] == "{2}") \
    |> aggregateWindow(every: 10s, fn: mean, createEmpty: false) \
    |> yield(name: "mean")'


# メイン関数   この関数は末尾のif文から呼び出される
def main():
    tables = FLUX_CLIENT.query_api().query(INFLUX_QUERY)
    for table in tables:
        print(len(table.records))
        for row in table.records:
            print (row.values)


    print(table.records[-1])
    time.sleep(10)


if __name__ == '__main__':          # importされないときだけmain()を呼ぶ
    parser = argparse.ArgumentParser()
    parser.add_argument("--infhost", type=str, default="localhost", help="hostname or ip")
    parser.add_argument("--inftoken", type=str, default="", help="token to write db")
    parser.add_argument("--infbucket", type=str, default="", help="bucketname")
    parser.add_argument("--sensorclient", type=str, default="", help="hostname of raspberrypi")
    
    args = parser.parse_args()
    INFLUX_HOST = INFLUX_HOST.format(args.infhost)
    INFLUX_TOKEN = args.inftoken
    INFLUX_BUCKET = args.infbucket
    SENSOR_CLIENT = args.sensorclient
    INFLUX_QUERY = INFLUX_QUERY.format(INFLUX_BUCKET, MEASUREMENT, SENSOR_CLIENT)
#    print(INFLUX_QUERY)
    FLUX_CLIENT = InfluxDBClient(url=INFLUX_HOST, token=INFLUX_TOKEN, org=INFLUX_ORG)
    
    while True:
        main()    # メイン関数を呼び出す
