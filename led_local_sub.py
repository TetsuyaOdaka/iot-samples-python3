'''
ローカルMQTTサーバ（ブリッジ）からサブスクライブする。

'''
import sys, os, re
import time
import json

import argparse

import paho.mqtt.client as mqtt     # MQTTのライブラリをインポート
from time import sleep              # 3秒間のウェイトのために使う

import RPi.GPIO as GPIO # RPi.GPIOモジュールを使用

CLIENT_ID = os.uname()[1] # クライアントID（ユニークでなければならないので注意）
MQTT_HOST = ""
MQTT_PORT = 1883
KEEP_ALIVE = 60
TOPIC = ""
QOS = 1

GPIO_LED = 17

# GPIO番号指定の準備
GPIO.setmode(GPIO.BCM)

# LEDピンを出力に設定
GPIO.setup(GPIO_LED, GPIO.OUT)
GPIO.output(GPIO_LED, 0)    # LED消灯

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
        _tmp = json.loads(msg.payload)
        _val = _tmp["value"]
        print("value : {}".format(_val))
        if _val < -3.0 or _val > 3.0:
            for i in range(2):
                GPIO.output(GPIO_LED, 1)    # LED点灯
                time.sleep(1)
                GPIO.output(GPIO_LED, 0)    # LED消灯
                time.sleep(1)
        else:
            GPIO.output(GPIO_LED, 0)    # LED消灯

        print("Received message '" + str(_tmp) + "' on topic '" + msg.topic + "' with QoS " + str(msg.qos))
    except:
        print("Json Error")

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
    parser.add_argument("--qos", type=int, default=1, help="0,1,2")
    
    args = parser.parse_args()
    MQTT_HOST = args.hostname
    MQTT_PORT = args.port
    KEEP_ALIVE = args.keepalive
    TOPIC = args.topic
    QOS = args.qos
    
    main()    # メイン関数を呼び出す
    # 後処理 GPIOを解放
    GPIO.cleanup(GPIO_LED)
