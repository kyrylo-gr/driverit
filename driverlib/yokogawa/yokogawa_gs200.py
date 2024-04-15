from typing import Literal, Optional

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
