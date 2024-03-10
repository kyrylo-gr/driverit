from typing import Literal

ONOFF_TYPE = Literal["ON", "OFF", 0, 1, True, False]


class ComunicationResultError(Exception):
    pass
