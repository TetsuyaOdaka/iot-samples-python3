'''
Lチカ

'''
import RPi.GPIO as GPIO # RPi.GPIOモジュールを使用
import time

# LEDとスイッチのGPIO番号
# デフォルトはRPZ-IR-Sensorの緑LEDと赤SW
# 必要に応じて変更
gpio_led = 17

# GPIO番号指定の準備
GPIO.setmode(GPIO.BCM)

# LEDピンを出力に設定
GPIO.setup(gpio_led, GPIO.OUT)

for i in range(10):
    GPIO.output(gpio_led, 1)    # LED点灯
    time.sleep(1)   
    GPIO.output(gpio_led, 0)    # LED消灯
    time.sleep(1)

# 後処理 GPIOを解放
GPIO.cleanup(gpio_led)
