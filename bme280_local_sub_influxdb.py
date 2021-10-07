'''
ローカルMQTTサーバ（ブリッジ）からサブスクライブしたデータをinfluxdbに入れる


'''
import sys, os, re
import time
import json

import argparse

import paho.mqtt.client as mqtt     # MQTTのライブラリをインポート
from time import sleep              # 3秒間のウェイトのために使う

from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import ASYNCHRONOUS

SCRIPT_NAME = os.path.basename(__file__)
CLIENT_ID = os.uname()[1] + "_" + SCRIPT_NAME # クライアントID（ユニークでなければならないので注意）
MQTT_HOST = ""
MQTT_PORT = 1883
KEEP_ALIVE = 60
TOPIC = ""
QOS = 1

INFLUX_HOST = "http://{}:8086"
INFLUX_TOKEN = ""
INFLUX_ORG = "pydev"
INFLUX_BUCKET = ""
MEASUREMENT = "bme280"
FLUX_CLIENT = None


# ブローカーに接続できたときの処理
def on_connect(client, userdata, flag, rc):
    print("Connected with result code " + str(rc))  # 接続できた旨表示
    return

# サブスクライブしたときの処理
def on_subscribe(client, userdata, mid, qos):
    print("Subscribe: {}, QOS: {} ".format(str(mid), str(qos)))  # 接続できた旨表示
    return

# ブローカーが切断したときの処理
def on_disconnect(client, userdata, rc):
    if  rc != 0:
        print("Unexpected disconnection. rc = {}".format(rc))
    else:
        print("Disconnected.")
    return

# メッセージが届いたときの処理
def on_message(client, userdata, msg):
    # msg.topicにトピック名が，msg.payloadに届いたデータ本体が入っている
    try:
        # msg.topicにトピック名が，msg.payloadに届いたデータ本体が入っている
        _tmp = json.loads(msg.payload)
        _wk = msg.topic.split('/')
        async_write_bme280(_tmp, _wk[2])
    except:
        print("Json Error")
    return

'''
    async write BME280
'''
def async_write_bme280(jdata, hostname):

    write_api = FLUX_CLIENT.write_api(write_options=ASYNCHRONOUS)

    _points = []
    _point = Point(MEASUREMENT).tag("hostname", hostname).field("temperature", jdata["temperature"])
    _points.append(_point)
    _point = Point(MEASUREMENT).tag("hostname", hostname).field("humidity", jdata["humidity"])
    _points.append(_point)
    _point = Point(MEASUREMENT).tag("hostname", hostname).field("pressure", jdata["pressure"])
    _points.append(_point)

    async_result = write_api.write(bucket=INFLUX_BUCKET, record=_points)
    async_result.get()
    LOGGER.debug("Write InfluxDB")

    return

# メイン関数   この関数は末尾のif文から呼び出される
def main():
    client = mqtt.Client()   # クラスのインスタンス(実体)の作成
    client.on_connect = on_connect         # 接続時のコールバック関数を登録
    client.on_disconnect = on_disconnect   # 切断時のコールバックを登録
    client.on_message = on_message         # メッセージ受信時
    client.on_subscribe = on_subscribe      # メッセージ受信時

    client.connect(MQTT_HOST, MQTT_PORT, KEEP_ALIVE)
    client.subscribe(TOPIC, QOS)            # サブスクライブ

    client.loop_forever()                   # 永久ループして待ち続ける

if __name__ == '__main__':          # importされないときだけmain()を呼ぶ
    parser = argparse.ArgumentParser()
    parser.add_argument("--hostname", type=str, default="localhost", help="hostname or ip")
    parser.add_argument("--port", type=int, default=1883, help="Port number override")
    parser.add_argument("--keepalive", type=int, default=60, help="")
    parser.add_argument("--topic", type=str, default="l2l/test", help="Targeted topic")
    parser.add_argument("--qos", type=int, default=1, help="qos=0 or 1 or 2")
    parser.add_argument("--infhost", type=str, default="localhost", help="hostname or ip")
    parser.add_argument("--inftoken", type=str, default="", help="token to write db")
    parser.add_argument("--infbucket", type=str, default="", help="bucketname")
    
    args = parser.parse_args()
    MQTT_HOST = args.hostname
    MQTT_PORT = args.port
    KEEP_ALIVE = args.keepalive
    TOPIC = args.topic
    QOS = args.qos
    INFLUX_HOST = INFLUX_HOST.format(args.infhost)
    INFLUX_TOKEN = args.inftoken
    INFLUX_BUCKET = args.infbucket
    FLUX_CLIENT = InfluxDBClient(url=INFLUX_HOST, token=INFLUX_TOKEN, org=INFLUX_ORG)
    
    main()    # メイン関数を呼び出す
