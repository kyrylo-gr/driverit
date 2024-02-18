from .visa_driver import VisaDriver


class Anapico(VisaDriver):
    def __init__(self, resource_location: str):
        super().__init__(resource_location, "\n")

    def get_frequency(self, channel):
        return float(self.ask(f":SOURce{int(channel)}:FREQuency:CW?"))

    def set_frequency(self, channel, value):
        self.write(f":SOURce{int(channel)}:FREQuency:CW {float(value)}")
        return self

    frequency = property(get_frequency, set_frequency)

    def get_power(self, channel):
        return float(self.ask(f":SOURce{int(channel)}:POWER?"))

    def set_power(self, channel, value):
        if value < -10:
            raise ValueError("Anapico cannot output less than -10 dBm")
        self.write(f":SOURce{int(channel)}:POWER {float(value)}")
        return self

    power = property(get_power, set_power)

    def get_rf_state(self, channel):
        return int(self.ask(f"OUTPut{int(channel)}:STATE?")[:1])

    def set_rf_state(self, channel, state):
        if state is True:
            state = "ON"
        else:
            state = "OFF"
        self.write(f"OUTPut{int(channel)}:STATE {state}")
        return self

    rf_state = property(get_rf_state, set_rf_state)
