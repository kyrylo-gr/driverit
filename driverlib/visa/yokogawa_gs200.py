from typing import Literal

from .visa_driver import ONOFF_TYPE, VisaDriver


class YokoGS200(VisaDriver):
    mode: Literal["current", "voltage"]

    def __init__(
        self,
        resource_location: str,
        mode: Literal["current", "voltage"] = "voltage",
    ):
        super().__init__(resource_location=resource_location)
        self.mode = mode

    @property
    def idn(self) -> str:
        return self.ask("*IDN?")

    def get_output(self) -> bool:
        return self.ask("OUTPUT?").strip() == "1"

    def set_output(self, value: ONOFF_TYPE):
        if self._value_to_bool(value):
            self.write("OUTPUT ON")
        else:
            self.write("OUTPUT OFF")

    output = property(get_output, set_output)

    def get_range(self) -> int:
        return float(self.ask(":SOURce:RANGe?").strip())

    def set_range(self, value: float):
        self.write(f":SOURce:RANGe {value:.4f}")

    range = property(get_range, set_range)

    def set_level(self, value: float):
        self.write(f":SOURce:Level {value:.4f}")

    def get_level(self) -> float:
        return float(self.ask(":SOURce:Level?"))

    level = property(get_level, set_level)
