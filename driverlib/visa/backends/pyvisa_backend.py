import logging
import sys
from typing import Optional

from pyvisa.highlevel import ResourceManager
from pyvisa.resources import Resource

from .backend_protocol import BackendProtocol


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
        self._resource.write_termination = self.write_termination  # type: ignore
        if self.timeout is not None:
            self._resource.timeout = self.timeout
        return self._resource

    def __exit__(self, *args):
        self._resource.close()


class PyVisaBackend(BackendProtocol):
    def __init__(
        self,
        resource_location=None,
        endline="",
        check: bool = False,
        logger: Optional[logging.Logger] = None,
        **kwargs,
    ):
        self.endline = endline
        if sys.platform.startswith("linux"):
            self.rm = ResourceManager("@py")
        elif sys.platform.startswith("win32"):
            self.rm = ResourceManager()
        else:
            self.rm = ResourceManager()

        self.resource_location = resource_location

        if logger is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)

        self.logger = logger

        if check:
            logger.info("Connected to %s", self.query("*IDN?"))
        elif logger.level <= logging.DEBUG:
            logger.debug("Connected to %s", self.query("*IDN?"))

    def write(self, message, timeout=None):
        with OpenResource(
            self.rm, self.resource_location, self.endline, timeout=timeout
        ) as resource:
            resource.write(message)  # type: ignore

    def query(self, message, timeout=None) -> str:
        with OpenResource(
            self.rm, self.resource_location, self.endline, timeout=timeout
        ) as resource:
            return resource.query(message).strip()  # type: ignore

    def read(self, timeout=None) -> str:
        with OpenResource(
            self.rm, self.resource_location, self.endline, timeout=timeout
        ) as resource:
            return resource.read().strip()  # type: ignore

    def write_and_read(self, message, timeout=None) -> str:
        with OpenResource(
            self.rm, self.resource_location, self.endline, timeout=timeout
        ) as resource:
            resource.write(message)  # type: ignore
            return resource.read().strip()  # type: ignore

    def close(self):
        """Close the connection to the device."""
        self.rm.close()
