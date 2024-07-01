from typing import Optional, Type

from .visa.backends.backend_protocol import BackendProtocol

visa_backend: Optional[Type[BackendProtocol]] = None


def get_backend() -> Type[BackendProtocol]:
    global visa_backend  # pylint: disable=W0603
    if visa_backend is None:
        from .visa.backends.pyvisa_backend import (  # noqa: F401 # pylint: disable=C0415
            PyVisaBackend,
        )

        visa_backend = PyVisaBackend
        return visa_backend
    return visa_backend


def set_backend(backend: Type[BackendProtocol]):
    global visa_backend  # pylint: disable=W0603
    visa_backend = backend
