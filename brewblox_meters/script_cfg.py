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

with open("config.json", "r") as f:
    cfg = json.load(f)
    print(cfg)


# Create a websocket MQTT client
client = mqtt.Client(transport='websockets')
client.ws_set_options(path='/eventbus')

ser = serial.Serial(port=cfg['_FLOWMETER_SERIAL_PORT'],
                    baudrate=115200,
                    timeout=1)


def main():
    try:
        # Create a websocket MQTT client
        client.connect_async(host=cfg['_HOST'], port=cfg['_PORT'])
        client.loop_start()

        while True:
            # Iterate through ads1 channels, populate dict d1
            d1 = {}
            for index, ads1_key in enumerate(cfg['_ADS_KEYS']['_ads1_keys']):
                m1 = Meter()
                m1.ads = ADS1115(address=0x48)
                m1.name = ads1_key

                d1[m1.name] = {
                    'mA': round(m1.read_ma(index), 2),
                    'pH': round(m1.ma_to_ph(m1.ma), 2),
                    'ORP': round(m1.ma_to_orp(m1.ma), 2)
                }

            # Iterate through ads2 channels, populate dict d2
            d2 = {}
            for index, ads2_key in enumerate(cfg['_ADS_KEYS']['_ads2_keys']):
                m2 = Meter()
                m2.ads = ADS1115(address=0x49)
                m2.name = ads2_key

                d2[m2.name] = {
                    'mA': round(m2.read_ma(index), 2),
                    'pH': round(m2.ma_to_ph(m2.ma), 2),
                    'ORP': round(m2.ma_to_orp(m2.ma), 2)
                }

            # Iterate through ads3 channels, populate dict d3
            d3 = {}
            for index, ads3_key in enumerate(cfg['_ADS_KEYS']['_ads3_keys']):
                v = VolumeSensor()
                v.name = ads3_key
                v.ads = ADS1115(address=0x4a)

                d3[v.name] = {
                    'adc': v.read_ads(index),
                    'trimmed-adc': v.trim_adc(v.adc, cfg['_ADC3_OFFSETS'][index]),
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

            # Specific topic for this script
            TOPIC = cfg['_HISTORY_TOPIC'] + cfg['_SERVICE_TOPIC']

            client.publish(TOPIC, json.dumps(message))
            print(json.dumps(message, sort_keys=False, indent=4))
            sleep(5)

    finally:
        ser.close()
        client.loop_stop


if __name__ == '__main__':
    main()
