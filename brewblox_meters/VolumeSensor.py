"""
Code example for publishing data to the Brewblox eventbus

Dependencies:
- paho-mqtt
"""

import json
from time import sleep

from paho.mqtt import client as mqtt

from ads1115 import ADS1115

# 172.17.0.1 is the default IP address for the host running the Docker container
# Change this value if Brewblox is installed on a different computer
HOST = '192.168.1.2'

# 80 is the default port for HTTP, but this can be changed in brewblox env settings.
PORT = 80

# This is a constant value. You never need to change it.
HISTORY_TOPIC = 'brewcast/history'
TOPIC = HISTORY_TOPIC + '/volume-sensor'

# Ads setup
ADS = ADS1115(address=0x4a)
ADS_FULLSCALE = 32767
GAIN = 2/3
ADS_MAX_V = 4.096 / GAIN




class VolumeSensor:
    def __init__(self) -> None:
        # Create a websocket MQTT client
        self.client = mqtt.Client(transport='websockets')
        self.client.ws_set_options(path='/eventbus')

        self.bit_max = ADS_FULLSCALE
        self.adsMaxV = ADS_MAX_V

        self.bitsPerGallon = 1675
        self.bitsPerLiter = 442.54

    def read_ads(self, channel) -> int:
        self.adc = ADS.read_adc(channel, gain=GAIN)
        return self.adc

    def trim_adc(self, adc, offset) -> int:
        self.trimmed_adc = adc - offset
        return self.trimmed_adc

    def read_volts(self, channel) -> float:
        self.volts = self.read_ads(channel) * ADS_MAX_V / ADS_FULLSCALE
        return self.volts

    def adc_to_volts(self) -> float:
        return self.adc * self.adsMaxV / self.bit_max

    def adc_to_gallons(self) -> float:
        return self.adc / self.bitsPerGallon

    def adc_to_liters(self) -> float:
        return self.adc / self.bitsPerLiter

    def set_offset(self, offset) -> None:
        self.offset = offset

    def run(self):
        try:
            self.client.connect_async(host=HOST, port=PORT)
            self.client.loop_start()

            while True:
                data = {}
                keys = ['liqr_volume', 'mash_volume', 'boil_volume']
                adc_offsets = [8000, 5824, 7120]

                for index, key in enumerate(keys):
                    self.name = key
                    self.ads = ADS

                    data[self.name] = {
                        'adc': self.read_ads(index),
                        'trimmed-adc': self.trim_adc(self.read_ads(index), adc_offsets[index]),
                        'volts': round(self.read_volts(index), 2),
                        'liters': round(self.adc_to_liters(), 2),
                        'gallons': round(self.adc_to_gallons(), 2)
                    }

                # MQTT message to send to brewblox
                message = {
                    'key': 'VolumeSensors',
                    'data': data
                }

                # Publish message
                self.client.publish(TOPIC, json.dumps(message))
                print(json.dumps(message, sort_keys=False, indent=4))
                sleep(5)

        finally:
            self.client.loop_stop()


if __name__ == '__main__':
    VolumeSensor().run()
