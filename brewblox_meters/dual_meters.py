''' main script '''

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

# Create a websocket MQTT client
client = mqtt.Client(transport='websockets')
client.ws_set_options(path='/eventbus')

''' ADS1115 STUFF '''
# ADS1115 names and addresses
# ads1 = ADS1115(address=0x48)  # ADDRESS -> GND
# ads2 = ADS1115(address=0x49)  # ADDRESS -> VDD
# ads3 = ADS1115(address=0x4a)  # ADDRESS -> SDA
# ads4 = ADS1115(address=0x4b)  # ADDRESS -> SDL
ads1 = ADS1115(address=0x48)  # ADDRESS -> GND
ads2 = ADS1115(address=0x49)  # ADDRESS -> VDD

# Max positive bits of ADS1115
ADS_FULLSCALE = 32768

GAIN = 2/3

volt_max = 4.096 / GAIN


class MeterOutput(object):
    '''Class for 4-20ma industrial meters'''

    def __init__(self, name) -> None:
        self.name = name

    def adc_to_volts(self, adc, volt_max, bit_max) -> None:
        return adc * volt_max / bit_max

    def volts_to_pH(self, volts) -> float:
        return volts * 2

    def volts_to_mA(self, volts) -> float:
        return volts * 4


try:
    client.connect_async(host=HOST, port=PORT)
    client.loop_start()

    while True:
        ''' Iterate through meter_1_output data '''
        # Dictionaries for data
        d1 = {}
        meter_1_outputs = ['output_1', 'output_2', 'output_3', 'output_4']

        for index, meter_1_output in enumerate(meter_1_outputs):
            # Initiate each meter_1_output with a name
            meter_1_output = MeterOutput(meter_1_outputs[index])

            # value to zero out adc reading if neccessary
            adc_trim = 75

            # read adc and trim if negative
            meter_1_output.adc = ads1.read_adc(index, gain=GAIN)
            meter_1_output.volts = meter_1_output.adc * volt_max / ADS_FULLSCALE
            meter_1_output.mA = meter_1_output.volts_to_mA(meter_1_output.volts)
            meter_1_output.pH = meter_1_output.volts_to_pH(meter_1_output.volts)

            d1[meter_1_output.name] = {
                'adc': round(meter_1_output.adc, 2),
                'volts': round(meter_1_output.volts, 2),
                'mA': round(meter_1_output.mA, 2),
                'pH': round(meter_1_output.pH, 2)
            }

        d2 = {}
        meter_2_outputs = ['output_1', 'output_2', 'output_3', 'output_4']

        for index, meter_2_output in enumerate(meter_2_outputs):
            # Initiate each meter_1_output with name, unit of measure, unit_max, and bit_max
            meter2_output = MeterOutput(meter_2_outputs[index])

            GAIN = 2/3
            volt_max = 4.096 / GAIN
            adc_trm = 16

            meter_1_output.adc = ads2.read_adc(index, gain=GAIN)
            meter_1_output.volts = meter_1_output.adc * volt_max / ADS_FULLSCALE
            meter_1_output.mA = meter_1_output.volts_to_mA(meter_1_output.volts)
            meter_1_output.pH = meter_1_output.volts_to_pH(meter_1_output.volts)

            d2[meter_1_output.name] = {
                'adc': round(meter_1_output.adc, 2),
                'volts': round(meter_1_output.volts, 2),
                'mA': round(meter_1_output.mA, 2),
                'pH': round(meter_1_output.pH, 2)
            }

        ''' Output '''
        message = {
            'key': 'meters',
            'data': {'meter_1': d1, 'meter_2': d2}
        }

        client.publish(TOPIC, json.dumps(message))
        print(json.dumps(message, sort_keys=False, indent=4))
        sleep(5)

finally:
    client.loop_stop
