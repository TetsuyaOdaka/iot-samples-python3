'''
    BME280で取得してデータを指定したローカルMQTTサーバ（ブリッジ）
    に対してパブリッシュする。

'''
import sys, os, re
import json

import argparse

import paho.mqtt.client as mqtt     # MQTTのライブラリをインポート
from time import sleep              # 3秒間のウェイトのために使う

import bme280_sample as BME280  # スイッチサイエンスのサンプルを修正したもの

CLIENT_ID = os.uname()[1] # クライアントID=ホスト名（ユニークでなければならないので注意）
MQTT_HOST = ""
MQTT_PORT = 1883
KEEP_ALIVE = 60
TOPIC = ""
QOS = 1
SLEEP = 3 # sec

# ブローカーに接続できたときの処理
def on_connect(client, userdata, flag, rc):
    print("Connected with result code " + str(rc))
    return

# ブローカーが切断したときの処理
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
    else:
        print("disconnected.")
    return

# publishが完了したときの処理
def on_publish(client, userdata, mid):
    print("publish: {0}".format(mid))
    return

# メイン関数   この関数は末尾のif文から呼び出される
def main():
    myBME280 = BME280.BME280()
    myBME280.setup()
    myBME280.get_calib_param()

    client = mqtt.Client(clean_session=True)                 # クラスのインスタンス(実体)の作成
    client.on_connect = on_connect         # 接続時のコールバック関数を登録
    client.on_disconnect = on_disconnect   # 切断時のコールバックを登録
    client.on_publish = on_publish         # メッセージ送信時のコールバック

    client.connect(MQTT_HOST, MQTT_PORT, KEEP_ALIVE)

    # 通信処理スタート
    client.loop_start()

    # 永久に繰り返す
    while True:
        # センサーからのデータの読み出し
        _d = myBME280.readData()
        _d["sensor"] = "BME280"
        # json.dumpsで正しいjsonにしてから投げるのがよい。
        _jd = json.dumps(_d)
        print(_jd)
        client.publish(TOPIC, _jd, QOS)    # トピック名とメッセージを決めて送信
        sleep(SLEEP)   # 3秒待つ

if __name__ == '__main__':          # importされないときだけmain()を呼ぶ
    parser = argparse.ArgumentParser()
    parser.add_argument("--hostname", type=str, default="localhost", help="hostname or ip")
    parser.add_argument("--port", type=int, default=1883, help="Port number override")
    parser.add_argument("--keepalive", type=int, default=60, help="")
    parser.add_argument("--topic", type=str, default="l2l/test", help="Targeted topic")
    parser.add_argument("--qos", type=int, default=1, help="0,1,2")
    parser.add_argument("--sleep", type=int, default=3, help="sleep time sec")

    args = parser.parse_args()
    MQTT_HOST = args.hostname
    MQTT_PORT = args.port
    KEEP_ALIVE = args.keepalive
    TOPIC = args.topic
    QOS = args.qos
    SLEEP = args.sleep

    main()    # メイン関数を呼び出す
