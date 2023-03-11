"""
main script
reads up to 4 ads1115 ADC boards outputs into one dictionary
publishes output to brewblox over mqtt
"""
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

# ADS1115 names and addresses
ads1 = ADS1115(address=0x48)  # ADDRESS -> GND
ads2 = ADS1115(address=0x49)  # ADDRESS -> VDD
ads3 = ADS1115(address=0x4a)  # ADDRESS -> SDA
ads4 = ADS1115(address=0x4b)  # ADDRESS -> SDL

# Max positive bits of ADS1115's 16 bit signed integer
ADS_FULLSCALE = 32767
GAIN = 2/3
ADS_MAX_V = 4.096 / GAIN

# Names of each input
ads1_keys = ['output1-1', 'output1-2', 'output1-3', 'output1-4']
ads2_keys = ['output2-1', 'output2-2', 'output2-3', 'output2-4']
ads3_keys = ['output3-1', 'output3-2', 'output3-3', 'output3-4']
ads4_keys = ['output4-1', 'output4-2', 'output4-3', 'output4-4']


def main():
    try:
        # Create a websocket MQTT client
        client.connect_async(host=HOST, port=PORT)
        client.loop_start()

        while True:
            # Iterate through ads1 channels, populate dict d1
            d1 = {}
            for index, ads1_key in enumerate(ads1_keys):
                m1 = Meter()
                m1.name = ads1_key
                m1.ads = ads1

                d1[m1.name] = {
                    'mA': round(m1.read_ma(index), 2),
                    'pH': round(m1.ma_to_ph(m1.ma), 2),
                    'ORP': round(m1.ma_to_orp(m1.ma), 2)
                }

            # Iterate through ads2 channels, populate dict d2
            d2 = {}
            for index, ads2_key in enumerate(ads2_keys):
                m2 = Meter()
                m2.name = ads2_key
                m2.ads = ads2

                d2[m2.name] = {
                    'mA': round(m2.read_ma(index), 2),
                    'pH': round(m2.ma_to_ph(m2.ma), 2),
                    'ORP': round(m2.ma_to_orp(m2.ma), 2)
                }

            # Iterate through ads3 channels, populate dict d3
            d3 = {}
            adc3_offsets = [8000, 5824, 6960, 6960]
            patch_list = [0, 0, 0, 0]
            for index, ads3_key in enumerate(ads3_keys):
                v = VolumeSensor()
                v.name = ads3_key
                v.ads = ads3

                d3[v.name] = {
                    'adc': v.read_ads(index),
                    'trimmed-adc': v.trim_adc(v.adc, adc3_offsets[index]),
                    'volts': round(v.read_volts(index), 2),
                    'liters': round(v.adc_to_liters(), 2),
                    'gallons': round(v.adc_to_gallons(), 2)
                }

                patch_list[index] = d3[v.name]['liters']

            # Output
            message = {
                'key': 'meters',
                'data': {'meter-1': d1,
                         'meter-2': d2,
                         'volume-sensors': d3}
            }

            client.publish(TOPIC, json.dumps(message))
            print(json.dumps(message, sort_keys=False, indent=4))

            # This is a constant value. You never need to change it.
            API_TOPIC = 'brewcast/spark/blocks'

            # We'll be using the 'patch' command
            # 'create', 'write', and 'delete' are also available
            # https://www.brewblox.com/dev/reference/blocks_api.html
            PATCH_TOPIC = API_TOPIC + '/patch'

            # IMPORTANT !!
            # Don't forget to first create the 'Tutorial Sensor' block
            # Patch writes to non-existent blocks will be ignored

            liqr_liters = {
                # The block ID
                'id': 'EXT_liqrLiters',

                # The unique service name
                'serviceId': 'spark-three',

                # https://www.brewblox.com/dev/reference/block_types.html#tempsensorexternal
                'type': 'TempSensorExternal',

                # We only write the field we want to change
                # Because we're using patch, the other settings will remain unchanged
                'data': {'setting[degC]': patch_list[0]},
            }

            mash_liters = {
                # The block ID
                'id': 'EXT_mashLiters',

                # The unique service name
                'serviceId': 'spark-three',

                # https://www.brewblox.com/dev/reference/block_types.html#tempsensorexternal
                'type': 'TempSensorExternal',

                # We only write the field we want to change
                # Because we're using patch, the other settings will remain unchanged
                'data': {'setting[degC]': patch_list[1]},
            }

            boil_liters = {
                # The block ID
                'id': 'EXT_boilLiters',

                # The unique service name
                'serviceId': 'spark-three',

                # https://www.brewblox.com/dev/reference/block_types.html#tempsensorexternal
                'type': 'TempSensorExternal',

                # We only write the field we want to change
                # Because we're using patch, the other settings will remain unchanged
                'data': {'setting[degC]': patch_list[2]},
            }

            client.publish(PATCH_TOPIC, json.dumps(liqr_liters))
            client.publish(PATCH_TOPIC, json.dumps(mash_liters))
            client.publish(PATCH_TOPIC, json.dumps(boil_liters))

            print(f'sent {liqr_liters, mash_liters, boil_liters}')

            sleep(5)

    finally:
        client.loop_stop


if __name__ == '__main__':
    main()
