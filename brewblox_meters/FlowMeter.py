"""
Code example for publishing data to the Brewblox eventbus

Dependencies:
- paho-mqtt
"""

import enum
import json
from time import sleep

import RPi.GPIO as GPIO
from paho.mqtt import client as mqtt

from ads1115 import ADS1115

# 172.17.0.1 is the default IP address for the host running the Docker container
# Change this value if Brewblox is installed on a different computer
HOST = '192.168.1.2'

# 80 is the default port for HTTP, but this can be changed in brewblox env settings.
PORT = 80

# This is a constant value. You never need to change it.
HISTORY_TOPIC = 'brewcast/history'
TOPIC = HISTORY_TOPIC + '/flowMeter'

# Max positive bits of ADS1115's 16 bit signed integer
ADS_FULLSCALE = 32767
GAIN = 2/3
ADS_MAX_V = 4.096 / GAIN

ads4 = ADS1115(address=0x4b)
ads4_keys = ['liquour_in', 'mash_underlet', 'sauergut']
FLOW_SENSOR_GPIO = 13


class FlowMeter:
    def __init__(self) -> None:
        # Create a websocket MQTT client
        self.client = mqtt.Client(transport='websockets')
        self.client.ws_set_options(path='/eventbus')

        self.bit_max = ADS_FULLSCALE
        self.adsMaxV = ADS_MAX_V

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(FLOW_SENSOR_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(FLOW_SENSOR_GPIO, GPIO.FALLING, callback=self.on_pulse)

    def on_pulse(self):
        if self.collecting:
            self.count += 1

    def run(self):
        try:
            self.client.connect_async(host=HOST, port=PORT)
            self.client.loop_start()

            while True:
                d4 = {}
                for index, ads4_key in enumerate(ads4_keys):
                    self.name = ads4_key
                    self.ads = ads4
                    self.adc = self.ads.read_adc(index, gain=GAIN)

                    self.count = 0
                    self.collecting = True
                    sleep(1)
                    self.collecting = False

                    # Pulse frequency (Hz) = 7.5Q, Q is flow rate in L/min.
                    self.Q = 8
                    self.flow = (self.count / self.Q)

                    d4[self.name] = {
                        'flow[l/min]' : round(self.flow, 2)
                    }

                # MQTT message to send to brewblox
                message = {
                    'key': 'flowMeter',
                    'data': d4
                }

                print(json.dumps(message))

                # Publish message
                self.client.publish(TOPIC, json.dumps(message))
                sleep(5)

        finally:
            self.client.loop_stop()
            GPIO.cleanup()


if __name__ == '__main__':
    FlowMeter().run()
