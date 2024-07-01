import logging
from typing import List, Optional

from ._backend_manager import BackendProtocol, get_backend
from .types import ONOFF_TYPE
from .utils import LimitedAttributeSetter


class VisaDriver(LimitedAttributeSetter):
    backend: BackendProtocol

    _possible_names: Optional[List[str]]
    _allow_attrs = ["logger", "backend"]

    def __init__(
        self,
        resource_location=None,
        endline="",
        check: bool = False,
        logger: Optional[logging.Logger] = None,
    ):
        if logger is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
        self.logger = logger

        self.backend: BackendProtocol = get_backend()(
            resource_location, endline, check=check, logger=logger
        )

    def write(self, message: str, timeout=None):
        self.backend.write(message, timeout=timeout)

    def ask(self, message, timeout=None) -> str:
        return self.backend.query(message, timeout=timeout)

    def read(self, timeout=None) -> str:
        return self.backend.read(timeout=timeout).strip()

    def write_and_read(self, message, timeout=None) -> str:
        self.backend.write(message, timeout=timeout)
        return self.backend.read(timeout=timeout)

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
        self.backend.close()

    @property
    def idn(self) -> str:
        """Retrieve the identification string.

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
