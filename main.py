'''
Author: Ailton Fidelix
Date: 10-10-2021
'''

from dht import DHT11
from collections import OrderedDict
from time import sleep
import machine as esp32
import urequests
import json
import wifimgr

sleep_time = 60

url = "http://0.0.0.0:8000/GroundSensor/"

dht = DHT11(esp32.Pin(4))
soil_sensor = esp32.ADC(esp32.Pin(32))
batt_sensor = esp32.ADC(esp32.Pin(33))

wlan = wifimgr.get_connection()

if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D


def translate(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    valueScaled = float(value - leftMin) / float(leftSpan)

    return int(rightMin + (valueScaled * rightSpan))


if esp32.reset_cause() == esp32.DEEPSLEEP_RESET:
    print('ESP - Woke from a deep sleep')

print('ESP - OK')

while True:

    dht.measure()
    device = wifimgr.device
    soil_humidity = translate(soil_sensor.read(), 0, 4095, 0, 100)
    air_humidity = dht.humidity()
    temperature = float(dht.temperature())
    battery_life = translate(batt_sensor.read(), 0, 4095, 0, 100)

    x = OrderedDict([('device', device), ('soil_humidity', soil_humidity), ('air_humidity',
                    air_humidity), ('temperature', temperature), ('battery_life', battery_life)])

    data = json.dumps(x)

    print('ESP - ' + data)

    try:
        urequests.put(url+device+'/', data=data)
        urequests.post(url, data=data)
        print('ESP - PUT success')
    except requests.exceptions.RequestException:
        print('ESP - PUT error')
        try:
            urequests.post(url, data=data)
            print('ESP - POST success')
        except requests.exceptions.RequestException:
            print('ESP - POST error')

    print('ESP - Sleep')
    esp32.deepsleep(sleep_time * 1000)
