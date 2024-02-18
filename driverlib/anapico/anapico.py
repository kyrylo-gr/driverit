from ..visa_driver import VisaDriver


class Anapico(VisaDriver):
    """
    A driver for controlling Anapico signal generators via the VISA interface.

    This class provides methods to control and query the Anapico signal generators, including setting and querying
    the frequency, power, and RF state of a specified channel.

    Args:
        resource_location (str): The VISA resource name used to connect to the device.

    """

    def __init__(self, resource_location: str):
        """Initialize the Anapico object with the specified resource location.

        The constructor configures the communication termination character as a newline character.

        Args:
            resource_location (str): The VISA resource name used to connect to the device.
        """
        super().__init__(resource_location, "\n")

    def get_frequency(self, channel):
        """Query the frequency of a specified channel.

        Args:
            channel: The channel number.

        Returns:
            float: The frequency of the specified channel in Hz.
        """
        return float(self.ask(f":SOURce{int(channel)}:FREQuency:CW?"))

    def set_frequency(self, channel, value):
        """Set the frequency of a specified channel.

        Args:
            channel: The channel number.
            value: The desired frequency in Hz.

        Returns:
            self: Returns the instance itself to allow for method chaining.
        """
        self.write(f":SOURce{int(channel)}:FREQuency:CW {float(value)}")
        return self

    frequency = property(get_frequency, set_frequency)

    def get_power(self, channel):
        """Query the power of a specified channel.

        Args:
            channel: The channel number.

        Returns:
            float: The power of the specified channel in dBm.
        """
        return float(self.ask(f":SOURce{int(channel)}:POWER?"))

    def set_power(self, channel, value):
        """Set the power of a specified channel.

        Args:
            channel: The channel number.
            value: The desired power in dBm. The Anapico cannot output less than -10 dBm.

        Returns:
            self: Returns the instance itself to allow for method chaining.

        Raises:
            ValueError: If the specified power value is less than -10 dBm.
        """
        if value < -10:
            raise ValueError("Anapico cannot output less than -10 dBm")
        self.write(f":SOURce{int(channel)}:POWER {float(value)}")
        return self

    power = property(get_power, set_power)

    def get_rf_state(self, channel):
        """Query the RF output state of a specified channel.

        Args:
            channel: The channel number.

        Returns:
            int: 1 if the RF output is enabled (on), 0 if disabled (off).
        """
        return int(self.ask(f"OUTPut{int(channel)}:STATE?")[:1])

    def set_rf_state(self, channel, state):
        """Set the RF output state of a specified channel.

        Args:
            channel: The channel number.
            state: The desired state. True to enable (on) the RF output, False to disable (off).

        Returns:
            self: Returns the instance itself to allow for method chaining.
        """
        if state is True:
            state = "ON"
        else:
            state = "OFF"
        self.write(f"OUTPut{int(channel)}:STATE {state}")
        return self

    rf_state = property(get_rf_state, set_rf_state)
