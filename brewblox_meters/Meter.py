import json
from time import sleep

from paho.mqtt import client as mqtt

from ads1115 import ADS1115

# Brewblox Host ip address
HOST = '192.168.1.2'

# Brewblox Port
PORT = 80

# The history service is subscribed to all topic starting with this
HISTORY_TOPIC = 'brewcast/history'

# Specific topic for this script
TOPIC = HISTORY_TOPIC + '/meters'

'''
ADS1115 names and addresses
ads1 = ADS1115(address=0x48)  # ADDRESS -> GND
ads2 = ADS1115(address=0x49)  # ADDRESS -> VDD
ads3 = ADS1115(address=0x4a)  # ADDRESS -> SDA
ads4 = ADS1115(address=0x4b)  # ADDRESS -> SDL
'''
ads1 = ADS1115(address=0x48)
ads2 = ADS1115(address=0x49)

# Max positive bits of ADS1115's 16 bit signed integer
ADS_FULLSCALE = 32767
GAIN = 2/3
ADS_MAX_V = 4.096 / GAIN

ads1_keys = ['mash_pH', 'boil_pH', 'mash_ORP', 'boil_ORP']
ads2_keys = ['inline_pH', 'liquor_pH', 'inline_ORP', 'liquor_ORP']

class Meter:
    def __init__(self) -> None:
        # Create a websocket MQTT client
        self.client = mqtt.Client(transport='websockets')
        self.client.ws_set_options(path='/eventbus')

        self.bit_max = ADS_FULLSCALE
        self.adsMaxV = ADS_MAX_V

    def read_ads(self, channel, offset=0) -> None:
        self.adc = self.ads.read_adc(channel, gain=GAIN) + offset

    def ma_to_ph(self, ma) -> float:
        return ma / 2

    def ma_to_volts(self, ma) -> float:
        return ma / 4

    def ma_to_orp(self, ma) -> float:
        return 400 - (ma * 28.57)

    def run(self):
        try:
            self.client.connect_async(host=HOST, port=PORT)
            self.client.loop_start()

            while True:
                ''' Iterate through ads1 channels and compile data'''
                d1 = {}
                for index, ads1_key in enumerate(ads1_keys):
                    self.name = ads1_key
                    self.ads = ads1
                    self.adc = self.ads.read_adc(index, gain=GAIN)
                    self.ma = self.adc * self.adsMaxV / self.bit_max * 4

                    d1[self.name] = {
                        'pH'   : round(self.ma_to_ph(self.ma), 2),
                        'ORP'  : round(self.ma_to_orp(self.ma), 2)
                    }

                ''' Iterate through ads1 channels and compile data'''
                d2 = {}
                for index, ads2_key in enumerate(ads2_keys):
                    self.name = ads2_key
                    self.ads = ads2
                    self.adc = self.ads.read_adc(index, gain=GAIN)
                    self.ma = self.adc * self.adsMaxV / self.bit_max * 4

                    d2[self.name] = {
                        'pH'   : round(self.ma_to_ph(self.ma), 2),
                        'ORP'  : round(self.ma_to_orp(self.ma), 2)
                    }

                ''' Output '''
                message = {
                    'key' : 'meters',
                    'data': {'meter_1': d1, 'meter_2': d2}
                }

                self.client.publish(TOPIC, json.dumps(message))
                print(json.dumps(message, sort_keys=False, indent=4))
                sleep(5)

        finally:
            self.client.loop_stop

if __name__ == '__main__':
    Meter().run()
