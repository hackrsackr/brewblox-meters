''' main script '''

import json
from time import sleep

from paho.mqtt import client as mqtt

from ads1115 import ADS1115
from analog_sensor import LevelSensor, MeterOutput
from kettle import BrewKettle

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
ads4 = ADS1115(address=0x4b)

# Max positive bits of ADS1115's 16 bit signed integer
ADS_FULLSCALE = 32767

GAIN = 2/3

boilKettle = BrewKettle()
mashKettle = BrewKettle()
liqrKettle = BrewKettle()

boil_liquidLevel = LevelSensor(boilKettle.max_volume_liters, ADS_FULLSCALE)    
mash_liquidLevel = LevelSensor(mashKettle.max_volume_liters, ADS_FULLSCALE)    
liqr_liquidLevel = LevelSensor(liqrKettle.max_volume_liters, ADS_FULLSCALE)

level_sensors = [boil_liquidLevel, mash_liquidLevel, liqr_liquidLevel]

for index, level_sensor in enumerate(level_sensors):
    level_sensor.adc     = ads1.read_adc(index, gain=GAIN)
    level_sensor.volts   = level_sensor.read_volts(level_sensor.adc)
    level_sensor.liters  = level_sensor.read_liters(level_sensor.adc)

    #print(level_sensor.liters)

ph1 = MeterOutput(10, ADS_FULLSCALE)
ph2 = MeterOutput(10, ADS_FULLSCALE)
ph3 = MeterOutput(10, ADS_FULLSCALE)
ph4 = MeterOutput(10, ADS_FULLSCALE)

meter_outputs = [ph1, ph2, ph3, ph4]

for index, meter_output in enumerate(meter_outputs):
    meter_output.adc     = ads1.read_adc(index, gain=GAIN) + 75
    meter_output.volts   = meter_output.read_volts(meter_output.adc)
    meter_output.ph  = meter_output.read_ph(meter_output.adc)

    print(index, meter_output.volts, meter_output.ph)

