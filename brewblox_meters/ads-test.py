import json

from ads1115 import ADS1115
from Meter import Meter
ads1 = ADS1115(address=0x48)
ads2 = ADS1115(address=0x49)
ads3 = ADS1115(address=0x4a)
ads4 = ADS1115(address=0x4b)

ADS_FULLSCALE = 32767
GAIN = 2/3
ADS_MAX_V = 4.096 / GAIN

print(ads1.read_adc(0, gain=GAIN))
print(ads1.read_adc(1, gain=GAIN))
print(ads1.read_adc(2, gain=GAIN))
print(ads1.read_adc(3, gain=GAIN))

print(ads2.read_adc(0, gain=GAIN))
print(ads2.read_adc(1, gain=GAIN))
print(ads2.read_adc(2, gain=GAIN))
print(ads2.read_adc(3, gain=GAIN))

print(ads3.read_adc(0, gain=GAIN))
print(ads3.read_adc(1, gain=GAIN))
print(ads3.read_adc(2, gain=GAIN))
print(ads3.read_adc(3, gain=GAIN))
