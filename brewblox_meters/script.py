import json
from time import sleep

from paho.mqtt import client as mqtt

from ads1115 import ADS1115
from Meter import Meter
from VolumeSensor import VolumeSensor

# Brewblox Host ip address
HOST = '192.168.1.2'

# Brewblox Port
PORT = 80

# The history service is subscribed to all topic starting with this
HISTORY_TOPIC = 'brewcast/history'

# Specific topic for this script
TOPIC = HISTORY_TOPIC + '/meters'

# Create a websocket MQTT client
client = mqtt.Client(transport='websockets')
client.ws_set_options(path='/eventbus')

'''
ADS1115 names and addresses
ads1 = ADS1115(address=0x48)  # ADDRESS -> GND
ads2 = ADS1115(address=0x49)  # ADDRESS -> VDD
ads3 = ADS1115(address=0x4a)  # ADDRESS -> SDA
ads4 = ADS1115(address=0x4b)  # ADDRESS -> SDL
'''
ads1 = ADS1115(address=0x48)
ads2 = ADS1115(address=0x49)
ads3 = ADS1115(address=0x4a)

# Max positive bits of ADS1115's 16 bit signed integer
ADS_FULLSCALE = 32767
GAIN = 2/3
ADS_MAX_V = 4.096 / GAIN

ads1_keys = ['mash_pH', 'boil_pH', 'mash_ORP', 'boil_ORP']
ads2_keys = ['inline_pH', 'liquor_pH', 'inline_ORP', 'liquor_ORP']
ads3_keys = ['liqr_volume', 'mash_volume', 'boil_volume']

adc3_offsets = [7984, 6553, 6672]

def run():
    try:
        client.connect_async(host=HOST, port=PORT)
        client.loop_start()

        while True:
            ''' Iterate through ads1 channels and compile data'''
            d1 = {}
            for index, ads1_key in enumerate(ads1_keys):
                m1 = Meter()
                m1.name = ads1_key
                m1.ads = ads1
                m1.adc = m1.ads.read_adc(index, gain=GAIN)
                m1.ma = m1.adc * ADS_MAX_V / ADS_FULLSCALE * 4

                d1[m1.name] = {
                    'pH'   : round(m1.ma_to_ph(m1.ma), 2),
                    'ORP'  : round(m1.ma_to_orp(m1.ma), 2)
                }

            ''' Iterate through ads1 channels and compile data'''
            d2 = {}
            for index, ads2_key in enumerate(ads2_keys):
                m2 = Meter()
                m2.name = ads2_key
                m2.ads = ads2
                m2.adc = m2.ads.read_adc(index, gain=GAIN)
                m2.ma = m2.adc * m2.adsMaxV / m2.bit_max * 4

                d2[m2.name] = {
                    'pH'   : round(m2.ma_to_ph(m2.ma), 2),
                    'ORP'  : round(m2.ma_to_orp(m2.ma), 2)
                }

            d3 ={}
            for index, ads3_key in enumerate(ads3_keys):
                v = VolumeSensor()
                v.name = ads3_key
                v.ads = ads3
                v.adc = v.read_ads(index, adc3_offsets[index])
                v.volts = v.adc * v.adsMaxV / v.bit_max

                d3[v.name] = {
                    'adc'     : v.adc,
                    'liters'  : round(v.adc_to_liters(), 2),
                    'gallons' : round(v.adc_to_gallons(), 2)
                }


            ''' Output '''
            message = {
                'key' : 'meters',
                'data': {'meter_1': d1, 'meter_2': d2, 'volume_sensors' : d3}
            }

            client.publish(TOPIC, json.dumps(message))
            print(json.dumps(message, sort_keys=False, indent=4))
            sleep(5)

    finally:
        client.loop_stop

if __name__ == '__main__':
    run()
