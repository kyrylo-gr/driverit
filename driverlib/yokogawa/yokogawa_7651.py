from ..types import ONOFF_TYPE, ComunicationResultError
from ..visa_driver import VisaDriver


class Yokogawa7651(VisaDriver):
    """
    A driver for controlling the Yokogawa 7651 source measure unit via VISA interface.

    This class provides an interface to control and query the Yokogawa 7651, including setting its
    output state, output range, and output level.

    Usage:
    -------
    ```

    from driverlib.yokogawa import Yokogawa7651

    yoko = Yokogawa7651("address")

    yoko.output = True
    yoko.voltage = 1.0
    ```
    """

    def get_voltage(self) -> float:
        data = self.ask("OD")
        return float(data[4::])

    # @test.this(value=test.float)
    def set_voltage(self, value: float):
        self.write("S{:+E}E".format(value))
        data = self.ask("OD")
        value = float(data[4::])
        # to avoid floating point rouding
        if abs(value - round(value, 9)) > 10**-9:
            raise ComunicationResultError(
                "Instrument did not set correctly the voltage"
            )

    voltage = property(get_voltage, set_voltage)

    def get_output(self) -> bool:
        mess = self.ask("OC")[5::]

        value = ("{0:08b}".format(int(mess)))[3]
        if value == "0":
            return False
        if value == "1":
            return True
        raise ComunicationResultError("Instrument did not return the output state")

    def set_output(self, value: ONOFF_TYPE):
        if self._value_to_bool(value):
            self.write("O1E")
            mess = self.ask("OC")[5::]
            if ("{0:08b}".format(int(mess)))[3] != "1":
                raise ComunicationResultError(
                    """Instrument did not set correctly the output"""
                )
        else:
            self.write("O0E")
            mess = self.ask("OC")[5::]  # Instr return STS1=m we want m
            if ("{0:08b}".format(int(mess)))[3] != "0":
                raise ComunicationResultError(
                    """Instrument did not set correctly the output"""
                )

    output = property(get_output, set_output)
