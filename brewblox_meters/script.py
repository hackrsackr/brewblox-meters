"""
main script
reads 4 ads1115 ADC boards outputs into one dictionary
publishes output to brewblox over mqtt
"""
import json
import serial

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

# USB port of esp32 thats reading flowmeters
FLOWMETER_SERIAL_PORT = '/dev/ttyUSB0'

ser = serial.Serial(port=FLOWMETER_SERIAL_PORT,
                    baudrate=115200,
                    timeout=1)


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

            d4 = {}
            flow_data = ser.readline().decode().rstrip()
            try:
                flow_data = json.loads(flow_data)
            except json.JSONDecodeError:
                continue
            d4 = flow_data

            # Output
            message = {
                'key': 'meters',
                'data': {'meter-1': d1,
                         'meter-2': d2,
                         'volume-sensors': d3,
                         'flow-meters': d4}
            }

            client.publish(TOPIC, json.dumps(message))
            print(json.dumps(message, sort_keys=False, indent=4))
            sleep(5)

    finally:
        ser.close()
        client.loop_stop


if __name__ == '__main__':
    main()
