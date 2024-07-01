import time
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

    _precision: int = 8
    default_safety_step: float = 0.02

    _max_level: Optional[float] = None
    _min_level: Optional[float] = None

    mode: Literal["current", "voltage"]

    def __init__(
        self,
        resource_location: str,
        mode: Literal["current", "voltage"] = "voltage",
        max_level: Optional[float] = None,
        min_level: Optional[float] = None,
    ):
        """Initialize the YokogawaGS200 object with the specified resource location and mode.

        Args:
            resource_location (str): The VISA resource name used to connect to the device.
            mode (Literal["current", "voltage"], optional): The initial operation mode of the GS200.
                Defaults to 'voltage'.
            max_level (Optional[float], optional): The maximum voltage/current value. Defaults to None.
            min_level (Optional[float], optional): The minimum voltage/current value. Defaults to None.
        """
        super().__init__(resource_location=resource_location)
        self.mode = mode
        self.set_limits(min_level, max_level)

    @property
    def min_level(self) -> Optional[float]:
        """Get or set the minimum voltage/current value."""
        return self._min_level

    @min_level.setter
    def min_level(self, value: Optional[float] = None):
        self._min_level = value

    @property
    def max_level(self) -> Optional[float]:
        """Get or set the maximum voltage value."""
        return self._max_level

    @max_level.setter
    def max_level(self, value: Optional[float] = None):
        self._max_level = value

    def set_limits(self, min_level: Optional[float], max_level: Optional[float]):
        """Set the minimum and maximum voltage/current values."""
        self._min_level = min_level
        self._max_level = max_level

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

    def get_range(self) -> float:
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
        if self.max_level is not None and value > self.max_level:
            raise ValueError(f"Level value {value} is greater than the maximum allowed value")
        if self.min_level is not None and value < self.min_level:
            raise ValueError(f"Level value {value} is smaller than the minimum allowed value")

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
        """Get the output voltage level."""
        return self.get_level("voltage")

    def set_voltage(self, value):
        """Set the output voltage level.

        Args:
            value (float): The desired output voltage level.
        """
        return self.set_level(value, "voltage")

    voltage = property(get_voltage, set_voltage)

    def get_current(self):
        """Get the output current level."""
        return self.get_level("current")

    def set_current(self, value):
        """Set the output current level.

        Args:
            value (float): The desired output current level.
        """
        return self.set_level(value, "current")

    current = property(get_current, set_current)

    def set_voltage_safely(self, value: float, step: Optional[float] = None):
        """Set the output voltage level safely.

        This method gradually changes the output voltage level from the current level to the desired level
        with a specified step size.

        Args:
            value (float): The desired output voltage level.
            step (float, optional): The step size for changing the voltage level.
                Defaults to self.default_safety_step.
        """
        if not self.output:
            raise ValueError("The output must be on")

        if step is None:
            step = self.default_safety_step

        initial_voltage = self.voltage
        if np.round(value, self._precision) == np.round(initial_voltage, self._precision):
            return

        step = abs(step) if initial_voltage < value else -abs(step)

        for v in np.arange(initial_voltage, value + step / 2, step):
            self.set_voltage(np.round(v, self._precision))
            time.sleep(0.2)
        return

    voltage_safely = property(get_voltage, set_voltage_safely)

    def set_output_safely(self, value: ONOFF_TYPE):
        """Set the output state safely.

        This method sets the voltage to 0 before setting the output to True.

        Args:
            value (ONOFF_TYPE): The desired output state. True to turn on the output, False to turn it off.
        """
        if self._value_to_bool(value):
            self.voltage = 0
            self.output = True
        else:
            self.output = False

    output_safely = property(None, set_output_safely)

    def set_output_voltage_safely(self, value: float, step: Optional[float] = None):
        """Set the output voltage level safely.

        This method sets the output state to True and then gradually changes the output voltage level
        from the current level to the desired level with a specified step size.

        Args:
            value (float): The desired output voltage level.
            step (float, optional): The step size for changing the voltage level. Defaults to None.
        """
        self.set_output_safely(True)
        self.set_voltage_safely(value, step)
