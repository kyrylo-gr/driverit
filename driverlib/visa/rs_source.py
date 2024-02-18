from .visa_driver import VisaDriver


class RhodeSchwarzSource(VisaDriver):
    """
    A driver for controlling Rohde & Schwarz signal generators via the VISA interface.

    This class provides methods to control and query the Rohde & Schwarz signal generators,
    including setting and querying the output power, frequency, and output state.

    Args:
        resource_location (str): The VISA resource name used to connect to the device.
    """

    def __init__(self, resource_location: str):
        """Initialize the RhodeSchwarzSource object with the specified resource location.

        The constructor configures the communication termination character as a newline character.

        Args:
            resource_location (str): The VISA resource name used to connect to the device.
        """
        super().__init__(resource_location, "\n")

    def get_power(self):
        """Query the output power of the signal generator.

        Returns:
            float: The output power in dBm.
        """
        return float(self.ask(":POW?"))

    def set_power(self, value):
        """Set the output power of the signal generator.

        Args:
            value (float): The desired output power in dBm.
        """
        self.write(":POW " + str(value))

    power = property(get_power, set_power)

    def get_frequency(self):
        """Query the frequency of the signal generator.

        Returns:
            float: The frequency in Hz.
        """
        return float(self.ask(":FREQ?"))

    def set_frequency(self, value):
        """Set the frequency of the signal generator.

        Args:
            value (float): The desired frequency in Hz.
        """
        self.write(":FREQ " + str(value))

    frequency = property(get_frequency, set_frequency)

    def get_output(self):
        """Query the output state of the signal generator.

        Returns:
            bool: True if the output is enabled, False otherwise.
        """
        return bool(int(self.ask("OUTP?")))

    def set_output(self, value):
        """Set the output state of the signal generator.

        Args:
            value (bool): The desired output state. True to enable the output, False to disable it.
        """
        if self._value_to_bool(value):
            self.write(":OUTP ON")
        else:
            self.write(":OUTP OFF")

    output = property(get_output, set_output)
