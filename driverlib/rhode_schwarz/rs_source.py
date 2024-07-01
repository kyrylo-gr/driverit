from typing import Literal

from ..types import ONOFF_TYPE
from ..visa_driver import VisaDriver


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
        self.write(f":FREQ {value:.0f}")

    frequency = property(get_frequency, set_frequency)

    def get_output(self) -> bool:
        """Query the output state of the signal generator.

        Returns:
            bool: True if the output is enabled, False otherwise.
        """
        return bool(int(self.ask("OUTP?")))

    def set_output(self, value: ONOFF_TYPE):
        """Set the output state of the signal generator.

        Args:
            value (bool | ON | OFF | 0 | 1): The desired output state. True to enable the output, False to disable it.
        """
        if self._value_to_bool(value):
            self.write(":OUTP ON")
        else:
            self.write(":OUTP OFF")

    output = property(get_output, set_output)

    def get_modulation(self) -> bool:
        """Query the modulation state the signal generator.

        Returns:
            bool: True if the modulation output is enabled, False otherwise.
        """
        return bool(int(self.ask("MOD:STAT?")))

    def set_modulation(self, value: ONOFF_TYPE):
        """Turn on or off the modulation output state of the signal generator.

        Args:
            value (bool | ON | OFF | 0 | 1): The desired output state. True to enable the output, False to disable it.
        """
        if self._value_to_bool(value):
            self.write("MOD:STAT ON")
        else:
            self.write("MOD:STAT OFF")

    modulation = property(get_modulation, set_modulation)

    def get_modulation_frequency(self):
        """Get the modulation frequency of the signal generator.

        Returns:
            float: Frequency of the modulation in Hz.
        """
        return float(self.ask("LFO1:FREQ?"))

    def set_modulation_frequency(self, value: float):
        """Set the modulation frequency of the signal generator.

        Args:
            value (float): The desired modulation frequency in Hz.
        """
        self.write(f"LFO1:FREQ {value}")

    modulation_frequency = property(get_modulation_frequency, set_modulation_frequency)

    def get_phase_modulation_state(self):
        """Query the phase modulation state of the signal generator.

        Returns:
            bool: True if phase modulation is enabled, False otherwise.
        """
        return bool(int(self.ask("PM:STAT?")))

    def set_phase_modulation_state(self, value: ONOFF_TYPE):
        """Set the phase modulation state of the signal generator.

        Args:
            value (bool | ON | OFF | 0 | 1): The desired phase modulation state.
                True to enable phase modulation, False to disable it.
        """
        if self._value_to_bool(value):
            self.write("PM:STAT ON")
        else:
            self.write("PM:STAT OFF")

    phase_modulation = property(get_phase_modulation_state, set_phase_modulation_state)

    def set_amplitude_modulation_state(self, value: ONOFF_TYPE):
        """Set the amplitude modulation state of the signal generator.

        Args:
            value (bool | ON | OFF | 0 | 1): The desired amplitude modulation state.
                True to enable amplitude modulation, False to disable it.
        """
        if self._value_to_bool(value):
            self.write("AM:STAT ON")
        else:
            self.write("AM:STAT OFF")

    def get_amplitude_modulation_state(self):
        """Query the amplitude modulation state of the signal generator.

        Returns:
            bool: True if amplitude modulation is enabled, False otherwise.
        """
        return bool(int(self.ask("AM:STAT?")))

    amplitude_modulation = property(get_amplitude_modulation_state, set_amplitude_modulation_state)

    def set_phase_modulation_source(self, value: Literal["INT", "EXT"]):
        """Set the phase modulation source of the signal generator.

        Args:
            value (Literal["INT", "EXT"]): The desired phase modulation source.
                Must be either "INT" or "EXT".
        """
        if value not in {"INT", "EXT"}:
            raise ValueError("Invalid value. Must be 'INT' or 'EXT'")
        self.write(f"PM:SOUR {value}")

    def get_phase_modulation_source(self):
        """Query the phase modulation source of the signal generator.

        Returns:
            str: The current phase modulation source. Either "INT" or "EXT".
        """
        return self.ask("PM:SOUR?")

    phase_modulation_source = property(get_phase_modulation_source, set_phase_modulation_source)
