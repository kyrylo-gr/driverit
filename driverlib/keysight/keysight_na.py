import time

import numpy as np
from pyvisa import VisaIOError

from ..visa_driver import VisaDriver


class KeysightNA(VisaDriver):
    def __init__(self, resource_location: str):
        super().__init__(resource_location, "\n")

    def get_curve(self):
        d = self.ask("CALC1:SEL:DATA:SDAT?")
        d = [float(f) for f in d.split(",")]
        d = np.array(d)
        real = d[::2]
        imag = d[1::2]
        return real + 1j * imag

    def get_frequencies(self):
        freqs = self.ask(":SENS1:FREQ:DATA?")
        freqs = [float(f) for f in freqs.split(",")]
        freqs = np.array(freqs)
        return freqs

    def get_power(self):
        return float(self.ask(":SOUR1:POW?"))

    def set_power(self, power):
        if power < -15:
            raise ValueError("Minimum power is -15 dBm")
        elif power > 0:
            raise ValueError("Maximum power is -5 dBm")
        self.write(f":SOUR1:POW {power}")

    power = property(get_power, set_power)

    def get_frequency_sweep(self) -> tuple[float, float, int]:
        f_min = self.ask(":SENS1:FREQ:STAR?")
        f_max = self.ask(":SENS1:FREQ:STOP?")
        n_freq = self.ask(":SENS1:SWE:POIN?")
        return float(f_min), float(f_max), int(n_freq)

    def set_frequency_sweep(self, f_min: float, f_max: float, n_freq: int):
        if n_freq > 10_001:
            raise ValueError("Maximum number of points is 10 001")
        self.write(f":SENS1:FREQ:STAR {f_min}")
        self.write(f":SENS1:FREQ:STOP {f_max}")
        self.write(f":SENS1:SWE:POIN {n_freq}")

    def set_if_bw(self, if_bw: float):
        if if_bw is None:
            self.write("SENS1:BWA")
        else:
            self.write(f"SENS1:BWID {int(if_bw)}")

    def get_if_bw(self):
        return float(self.ask("SENS1:BWID?"))

    if_bw = property(get_if_bw, set_if_bw)

    def set_averaging(self, n_ave: int):
        if n_ave == 1:
            self.write(":SENS1:AVER OFF")
        else:
            self.write(":SENS1:AVER ON")
            self.write(f":SENS1:AVER:COUN {n_ave}")
            self.write(":TRIG:AVER ON")

    def is_completed(self):
        try:
            return self.ask("*OPC?")  # Can make "beep" at end of measure
        except VisaIOError:
            return False

    def set_continuous_mode(self):
        self.write(":TRIG:SOUR INT")
        self.write(":INIT1:CONT ON")

    def setup_trigger_for_sweep(self):
        self.write(":INIT1:CONT ON")
        self.write(":TRIG:SOUR BUS")

    def setup_sweep(
        self,
        f_min: float,
        f_max: float,
        n_freq: int,
        power: float,
        if_bw: int = None,
        n_ave: int = 1,
        meas: str = "S21",
    ):
        # self.write("*RST")

        self.setup_trigger_for_sweep()

        assert meas in ["S11", "S21"]  # , "S12", "S22"]
        self.write(f":CALC:PAR:DEF {meas}")

        self.set_frequency_sweep(f_min, f_max, int(n_freq))
        self.set_power(power)
        self.set_if_bw(if_bw)
        self.set_averaging(int(n_ave))

    def measure(self, *args, **kwargs):
        if kwargs:
            self.setup_sweep(*args, **kwargs)
        else:
            self.setup_trigger_for_sweep()
        self.write(":TRIG:SING")
        while not self.is_completed():
            time.sleep(1e-3)
        data = self.get_curve()
        return data

    def get_output(self) -> True:
        """Query the output state of the signal generator.

        Returns:
            bool: True if the output is enabled, False otherwise.
        """
        return bool(int(self.ask("OUTP?")))

    def set_output(self, value):
        """Set the output state of the signal generator.

        Args:
            value (bool | ON | OFF | 0 | 1): The desired output state. True to enable the output, False to disable it.
        """
        if self._value_to_bool(value):
            self.write(":OUTP ON")
        else:
            self.write(":OUTP OFF")

    output = property(get_output, set_output)

    def get_sweep_time(self):
        return float(self.ask(":SENS1:SWE:TIME?"))
