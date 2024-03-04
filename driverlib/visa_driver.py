import logging
import sys
from typing import List, Optional

from pyvisa import VisaIOError
from pyvisa.highlevel import ResourceManager
from pyvisa.resources import Resource

from .types import ONOFF_TYPE
from .utils import LimitedAttributeSetter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OpenResource:
    rm: ResourceManager
    resource_location: str
    write_termination: str
    _resource: Resource
    timeout: Optional[int]

    def __init__(
        self,
        rm: ResourceManager,
        resource_location,
        write_termination="\n",
        timeout: Optional[int] = None,
    ):
        self.rm = rm
        self.resource_location = resource_location
        self.write_termination = write_termination
        self.timeout = timeout

    def __enter__(self) -> Resource:
        self._resource = self.rm.open_resource(
            self.resource_location, open_timeout=1000
        )
        self._resource.write_termination = self.write_termination
        if self.timeout is not None:
            self._resource.timeout = self.timeout
        return self._resource

    def __exit__(self, *args):
        self._resource.close()


class VisaDriver(LimitedAttributeSetter):

    _possible_names: Optional[List[str]]
    _allow_attrs = ["rm", "resource_location", "endline"]

    def __init__(self, resource_location=None, endline="", check: bool = False):
        self.endline = endline
        if sys.platform.startswith("linux"):
            self.rm = ResourceManager("@py")
        elif sys.platform.startswith("win32"):
            self.rm = ResourceManager()
        else:
            self.rm = ResourceManager()

        if resource_location is None:
            self.lookup_resources()
            return

        self.resource_location = resource_location

        if logger.level <= logging.DEBUG or check:
            logger.debug("Connected to %s", self.ask("*IDN?"))

    def write(self, message, timeout=None):
        with OpenResource(
            self.rm, self.resource_location, self.endline, timeout=timeout
        ) as resource:
            resource.write(message)  # + "\n")

    def ask(self, message, timeout=None) -> str:
        with OpenResource(
            self.rm, self.resource_location, self.endline, timeout=timeout
        ) as resource:
            return resource.query(message)

    def read(self, timeout=None) -> str:
        with OpenResource(
            self.rm, self.resource_location, self.endline, timeout=timeout
        ) as resource:
            return resource.read()

    def write_and_read(self, message, timeout=None) -> str:
        with OpenResource(
            self.rm, self.resource_location, self.endline, timeout=timeout
        ) as resource:
            resource.write(message)
            return resource.read()

    def _value_to_bool(self, value: ONOFF_TYPE):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() == "on":
                return True
            if value.lower() == "off":
                return False
            raise ValueError("Invalid value to convert to bool. Must be 'ON' or 'OFF'")
        if isinstance(value, int):
            if value == 0:
                return False
            if value == 1:
                return True
            raise ValueError("Invalid value to convert to bool. Must be 0 or 1")

        raise ValueError(
            "Invalid value to convert to bool. Must be int, bool or str ('ON' or 'OFF')"
        )

    def close(self):
        """Close the connection to the device."""
        self.rm.close()

    @property
    def idn(self) -> str:
        """Retrieve the identification string of the Yokogawa GS200.

        Returns:
            str: The identification string of the device.
        """
        return self.ask("*IDN?")

    def get_error(self):
        """Retrieve the error message from the device.

        Returns:
            str: The error message.
        """
        return self.ask("SYST:ERR?")

    def print_error(self):
        """Print eventual errors occurred."""
        print(f"Errors: {self.get_error()}", end="")

    def reset(self):
        """Reset instrument to factory default state. Does not clear volatile memory."""
        self.write("*RST")
        self.write("*WAI")

    def clear(self):
        """Clear event register, error queue -when power is cycled-."""
        self.write("*CLS")
        self.write("*WAI")

    def lookup_resources(self):
        """Look for all the available resources."""
        instruments = self.rm.list_resources()
        print(f"Found {len(instruments)} instruments:")
        for location in instruments:
            try:
                with OpenResource(self.rm, location, self.endline) as instr:
                    idn = instr.query("*IDN?")
            except VisaIOError:
                idn = None

            print(
                f"Resource named: {idn if idn else 'Unable to determine'} @ '{location}'"
            )
