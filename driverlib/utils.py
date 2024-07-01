from typing import Any


class LimitedAttributeSetter:
    def __setattr__(self, __name: str, __value: Any) -> None:
        if (
            hasattr(self, __name)
            or __name in self.__annotations__  # pylint: disable=no-member
            or (hasattr(self, "_allow_attrs") and __name in self._allow_attrs)  # type: ignore  # pylint: disable=E1101
        ):
            super().__setattr__(__name, __value)
            return
        raise TypeError(f"There is no such attribute '{__name}'")
