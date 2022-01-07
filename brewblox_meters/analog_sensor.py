'''
    AnalogSensor Class and sub classes for reading sensors.
'''
class AnalogSensor(object):
    '''Generic class for AnalogSensors'''

    def __init__(self, unit_max, bit_max) -> None:
        self.unit_max = unit_max
        self.bit_max = bit_max


class PressureSensor(AnalogSensor):
    '''Subclass of AnalogSensor for [.5-4.5v] pressure transducers'''

    def __init__(self, unit_max, bit_max) -> None:
        super(PressureSensor, self).__init__(unit_max, bit_max)

    def get_psi(self, adc) -> float:
        '''Get 0.5-4.5Vdc output from pressure transducers convert to PSI'''
        return (adc - self.bit_max * .1) * self.unit_max / (self.bit_max * .8)

    def set_psi(self, psi, trim) -> None:
        '''Add psi to Spunder instance'''
        self.psi = psi + trim if psi + trim >= 0 else 0


class LevelSensor(AnalogSensor):
    '''Subclass of AnalogSensor for liquid level sensors 0-5Vdc output'''

    def __init__(self, unit_max, bit_max) -> None:
        super(LevelSensor, self).__init__(unit_max, bit_max)
        self.ads_gain = 2/3
        self.ads_volt_max = 4.096 / self.ads_gain
        self.signal_volt_max = 5.0

    def read_volts(self, adc) -> float:
        return adc * self.volt_max / self.bit_max

    def read_liters(self, adc) -> float:
        #return adc * self.unit_max / self.bit_max
        return adc * self.ads_volt_max / self.bit_max * self.unit_max / self.signal_volt_max

    def read_gallons(self, adc) -> float:
        #return adc * self.unit_max / 3.785 / self.bit_max
        return adc * self.ads_volt_max / self.bit_max * self.unit_max / self.signal_volt_max / 3.785


class FlowMeter(AnalogSensor):
    '''Subclass of AnalogSensor for 5v flow meters'''

    def __init__(self, unit_max, bit_max) -> None:
        super(FlowMeter, self).__init__(unit_max, bit_max)

    def get_flow_rate(self, adc) -> float:
        '''Get data from flow meters, and output it in ml/t'''
        return (adc - self.bit_max * .1) * self.unit_max / (self.bit_max * .8)


class MeterOutput(AnalogSensor):
    '''Class for 4-20ma industrial meters'''

    def __init__(self, unit_max, bit_max) -> None:
        super(MeterOutput, self).__init__(unit_max, bit_max)
        self.ma_max = 20.0
        self.ads_gain = 2/3
        self.ads_volt_max = 4.096 / self.ads_gain
        self.signal_volt_max = 5.0

    def read_ma(self, adc) -> float:
        return adc * self.ma_max / self.bit_max

    def read_volts(self, adc) -> None:
        return adc * self.ads_volt_max / self.bit_max

    def read_ph(self, adc) -> float:
        return adc * self.ads_volt_max / self.bit_max * self.unit_max / self.signal_volt_max

    def read_orp(self, adc) -> float:
        return 400 - (adc * self.ma_max / self.bit_max * 28.57)
