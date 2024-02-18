from .visa_driver import VisaDriver


class RhodeSchwarzSource(VisaDriver):
    def __init__(self, resource_location: str):
        super().__init__(resource_location, "\n")

    def get_power(self):
        return float(self.ask(":POW?"))

    def set_power(self, value):
        self.write(":POW " + str(value))

    power = property(get_power, set_power)

    def get_frequency(self):
        return float(self.ask(":FREQ?"))

    def set_frequency(self, value):
        self.write(":FREQ " + str(value))

    frequency = property(get_frequency, set_frequency)

    def get_output(self):
        return bool(int(self.ask("OUTP?")))

    def set_output(self, value):
        if self._value_to_bool(value):
            self.write(":OUTP ON")
        else:
            self.write(":OUTP OFF")

    output = property(get_output, set_output)
