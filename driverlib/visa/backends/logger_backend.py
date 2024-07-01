import logging
from typing import Optional

from .backend_protocol import BackendProtocol


class LoggerBackend(BackendProtocol):
    def __init__(self, *_, logger: Optional[logging.Logger] = None, **__):
        if logger is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)

        self.logger = logger

    def write(self, message, timeout=None):
        self.logger.info("Write: %s.", message)

    def query(self, message, timeout=None) -> str:
        self.logger.info("Query: %s.", message)
        return "0"

    def read(self, timeout=None) -> str:
        self.logger.info("Read.")
        return "0"

    def write_and_read(self, message, timeout=None) -> str:
        self.logger.info("Query: %s.", message)
        return "0"

    def close(self):
        """Close the connection to the device."""
        self.logger.info("Close.")
