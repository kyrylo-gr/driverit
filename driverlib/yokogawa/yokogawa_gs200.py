import time
import warnings
from typing import Literal, Optional

import numpy as np

from ..visa_driver import ONOFF_TYPE, VisaDriver


class YokogawaGS200(VisaDriver):
    """A driver for controlling the Yokogawa GS200 source measure unit via VISA interface.

    This class provides an interface to control and query the Yokogawa GS200, including setting its operation mode,
    output state, output range, and output level. The device can operate in either current or voltage mode.

    Usage:
    -------
    ```

    from driverlib.yokogawa import YokogawaGS200

    yoko = YokogawaGS200("address")

    yoko.output = True
    yoko.voltage = 1.0
    ```

    """

    _precision = 8

    mode: Literal["current", "voltage"]

    def __init__(
        self,
        resource_location: str,
        mode: Literal["current", "voltage"] = "voltage",
    ):
        """Initialize the YokogawaGS200 object with the specified resource location and mode.

        Args:
            resource_location (str): The VISA resource name used to connect to the device.
            mode (Literal["current", "voltage"], optional): The initial operation mode of the GS200.
                Defaults to 'voltage'.
        """
        super().__init__(resource_location=resource_location)
        self.mode = mode

    def get_output(self) -> bool:
        """Query the output state of the Yokogawa GS200.

        Returns:
            bool: True if the output is on, False otherwise.
        """
        return self.ask("OUTPUT?").strip() == "1"

    def set_output(self, value: ONOFF_TYPE):
        """Set the output state of the Yokogawa GS200.

        Args:
            value (ONOFF_TYPE): The desired output state. True to turn on the output, False to turn it off.
        """
        if self._value_to_bool(value):
            self.write("OUTPUT ON")
        else:
            self.write("OUTPUT OFF")

    output = property(get_output, set_output)

    def get_range(self) -> int:
        """Query the output range of the Yokogawa GS200.

        Returns:
            int: The current output range setting of the device.
        """
        return float(self.ask(":SOURce:RANGe?").strip())

    def set_range(self, value: float):
        """Set the output range of the Yokogawa GS200.

        Args:
            value (float): The desired output range.
        """
        self.write(f":SOURce:RANGe {value:.4f}")

    range = property(get_range, set_range)

    def set_level(self, value: float, check_mode: Optional[str] = None):
        """Set the output level of the Yokogawa GS200.

        Args:
            value (float): The desired output level.
        """
        if check_mode is not None and self.mode != check_mode:
            raise TypeError(
                f"Yoko is configured in {self.mode} mode, while it should be {check_mode}"
            )

        self.write(f":SOURce:Level {value:.8f}")

    def get_level(self, check_mode: Optional[str] = None) -> float:
        """Query the output level of the Yokogawa GS200.

        Returns:
            float: The current output level of the device.
        """
        if check_mode is not None and self.mode != check_mode:
            raise TypeError(
                f"Yoko is configured in {self.mode} mode, while it should be {check_mode}"
            )
        return float(self.ask(":SOURce:Level?"))

    level = property(get_level, set_level)

    def get_voltage(self):
        return self.get_level("voltage")

    def set_voltage(self, value):
        return self.set_level(value, "voltage")

    voltage = property(get_voltage, set_voltage)

    def get_current(self):
        return self.get_level("current")

    def set_current(self, value):
        return self.set_level(value, "current")

    current = property(get_current, set_current)

    def set_voltage_safely(self, value: float, step: Optional[float] = None):
        """Set gradually the voltage from initial value to a given value"""
        if not self.output:
            raise ValueError("The output must be on")

        if step is None:
            step = 0.02

        init = self.voltage
        if np.round(value, self._precision) == np.round(init, self._precision):
            return True

        step = abs(step) if init < value else -abs(step)

        for v in np.arange(init, value + step / 2, step):
            # print(np.round(v, self._precision))
            self.set_voltage(np.round(v, self._precision))
        return True

    def set_output_safely(self, value: ONOFF_TYPE):
        """Set the voltage to 0 before setting the output to True."""
        if self._value_to_bool(value):
            if self.output:
                return False
            self.voltage = 0
            self.output = True
        else:
            self.output = False

    def set_output_voltage_safely(self, value: float, step: Optional[float] = None):
        """Set the output to on and set safely the voltage to value with given step."""
        self.set_output_safely(1)
        self.set_voltage_safely(value, step)

    def bring_to_voltage(self, value, n_tries: int = 0):
        """Slowly goes from current voltage to the new voltage"""
        """If voltage in the end is 0, output turns off"""
        """n_tries is for inside use, don't change unless you're sure"""

        assert (
            value <= 1.08 and value >= -1.08
        ), "voltage must be between 1.08 and -1.08"

        if self.output and self.voltage == value:
            return None

        if not self.output and self.voltage != 0:
            self.voltage = 0

        if self.voltage == 0 and value == 0:
            return None

        self.output = True
        ini = self.voltage
        target = ini
        step = 0.02

        if np.abs(value - ini) <= step:
            self.voltage = value
        else:
            for v in np.arange(
                ini,
                value + np.sign(value - ini) * step,
                np.sign(value - ini) * step,
            ):
                if np.sign(v) == 1:
                    target = np.ceil(1000 * v) / 1000
                elif np.sign(v) == -1:
                    target = np.floor(1000 * v) / 1000

                self.voltage = target
                time.sleep(0.2)
                if target == value:
                    break

            if value == 0 and np.abs(self.voltage) <= step * 3 / 2:
                self.output = False
        n_tries = n_tries + 1
        if self.voltage != value:
            if n_tries < 10:
                self.bring_to_voltage(value, n_tries)
            else:
                print("Couldn't get to precise voltage value after 10 tries!")
