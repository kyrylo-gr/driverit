from pyvisa.highlevel import Resource, ResourceManager

from ..types import ONOFF_TYPE
from ..utils import LimitedAttributeSetter

# from pyvisa import VisaIOError


class OpenResource:
    rm: ResourceManager
    resource_location: str
    write_termination: str
    _driver: Resource

    def __init__(self, rm: ResourceManager, resource_location, write_termination="\n"):
        self.rm = rm
        self.resource_location = resource_location
        self.write_termination = write_termination

    def __enter__(self):
        self._driver = self.rm.open_resource(self.resource_location, open_timeout=1000)
        self._driver.write_termination = self.write_termination
        return self._driver

    def __exit__(self, *args):
        self._driver.close()


class VisaDriver(LimitedAttributeSetter):
    def __init__(self, resource_location, endline=""):
        self.rm = ResourceManager()
        self.resource_location = resource_location
        self.endline = endline

    def write(self, message):
        with OpenResource(self.rm, self.resource_location, self.endline) as driver:
            driver.write(message)  # + "\n")

    def ask(self, message):
        with OpenResource(self.rm, self.resource_location, self.endline) as driver:
            return driver.query(message)

    def read(self):
        with OpenResource(self.rm, self.resource_location, self.endline) as driver:
            return driver.read()

    def write_and_read(self, message):
        with OpenResource(self.rm, self.resource_location, self.endline) as driver:
            driver.write(message)
            return driver.read()

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
