''' main script '''

import json
from time import sleep

#from paho.mqtt import client as mqtt

from ads1115 import ADS1115
from analog_sensor import LevelSensor
from kettle import BrewKettle

'''
ADS1115 names and addresses
ads1 = ADS1115(address=0x48)  # ADDRESS -> GND
ads2 = ADS1115(address=0x49)  # ADDRESS -> VDD
ads3 = ADS1115(address=0x4a)  # ADDRESS -> SDA
ads4 = ADS1115(address=0x4b)  # ADDRESS -> SDL
'''
ads = ADS1115(address=0x4a)

# Max positive bits of ADS1115's 16 bit signed integer
ADS_FULLSCALE = 32767
GAIN = 2/3

# init kettles for max_volume
liqrKettle = BrewKettle()
mashKettle = BrewKettle()
boilKettle = BrewKettle()

liqr_levelSensor = LevelSensor(liqrKettle.max_volume_liters, ADS_FULLSCALE)
mash_levelSensor = LevelSensor(mashKettle.max_volume_liters, ADS_FULLSCALE)
boil_levelSensor = LevelSensor(boilKettle.max_volume_liters, ADS_FULLSCALE)

level_sensors = [liqr_levelSensor, mash_levelSensor, boil_levelSensor]
level_sensors_names = ['liqr_volume', 'mash_volume', 'boil_volume']
offsets = [7984, 6553, 6672]

d = {}

while True:
    for index, level_sensor in enumerate(level_sensors):
        level_sensor.name = level_sensors_names[index]
        level_sensor.adc = ads.read_adc(index, gain=GAIN)
        level_sensor.maxVol = level_sensor.unit_max

        d[level_sensor.name] = {
            'adc'      : level_sensor.adc,
            'max_vol'  : round(level_sensor.unit_max, 2),
            'volts'    : round(level_sensor.read_volts(level_sensor.adc), 2),
            'gallons'  : round((level_sensor.adc - offsets[index]) / 1675, 2),
         #   'gallons'  : round(level_sensor.read_gallons(level_sensor.adc, offsets[index]), 2)
            'liters'    : round(level_sensor.read_liters(level_sensor.adc, offsets[index]), 2)
        }

    message = {
        'key' : 'level_sensors',
        'data': d
    }
    print(json.dumps(message, sort_keys=False, indent=4))
    sleep(5)
