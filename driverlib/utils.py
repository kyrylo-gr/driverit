from typing import Any


class LimitedAttributeSetter:
    def __setattr__(self, __name: str, __value: Any) -> None:
        if hasattr(self, __name):
            super().__setattr__(__name, __value)
            return
        raise TypeError(f"There is no such attribute '{__name}'")
