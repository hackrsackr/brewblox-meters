import math

class BrewKettle(object):
    '''Class to represent dimensions of kettles for volume measurement'''

    def __init__(self) -> None:
        self.height_cm = 43.18
        self.width_cm = 36.00
        self.radius_cm = self.width_cm / 2
        self.max_volume_cm3 = math.pi * pow(self.radius_cm, 2) * self.height_cm
        self.max_volume_liters = self.max_volume_cm3 / 1000.0
        self.max_volume_gallons = self.max_volume_liters / 3.785

