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
