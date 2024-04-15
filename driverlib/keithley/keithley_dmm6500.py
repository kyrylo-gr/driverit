from typing import Union

from ..types import ONOFF_TYPE
from ..visa_driver import VisaDriver


class KeithleyDMM6500(VisaDriver):
    """Driver for a Digital Multimeter (DMM6500) by Keithley Instruments.

    Args:
        VisaDriver (_type_): _description_

    Documentation: https://www.tek.com/-/media/files/dmm6500-900-01b_user_aug_2019.pdf
    """

    _mode = "VOLT:DC"

    def read_voltage(self):
        if self._mode != "VOLT:DC":
            raise ValueError("Invalid mode")
        return self.value

    def get_mode(self):
        return self.ask(":SENS:FUNC?")

    def set_mode(self, mode):
        return self.write(f':SENS:FUNC "{mode}"')

    mode = property(get_mode, set_mode)

    def get_range(self):
        return self.ask(":SENS:VOLT:RANG?")

    def set_range(self, range):
        self.write(f":SENS:VOLT:RANG {range}")

    range = property(get_range, set_range)

    @property
    def value(self):
        value: str = self.ask(":READ?")
        return float(value)

    def get_average(self):
        is_averaging = self._get_average_on()
        if not is_averaging:
            return 0
        return self._get_average_count()

    def set_average(self, value: Union[int, ONOFF_TYPE]):
        if isinstance(value, int) and value > 0:
            self._set_average_on(1)
            self._set_average_count(value)
            return
        self._set_average_on(value)

    average = property(get_average, set_average)

    def _get_average_on(self) -> bool:
        return self.ask(":SENS:VOLT:AVER?") == "1"

    def _set_average_on(self, mode: ONOFF_TYPE) -> bool:
        mode_: str = "1" if self._value_to_bool(mode) else "0"
        self.write(f":SENS:VOLT:AVER {mode_}")

    def _get_average_count(self) -> int:
        return int(self.ask(":SENS:VOLT:AVER:COUN?"))

    def _set_average_count(self, count: int) -> bool:
        self.write(f":SENS:VOLT:AVER:COUN {count}")
