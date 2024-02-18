import numpy as np

from .visa_driver import VisaDriver


class AgilentSA(VisaDriver):
    def __init__(self, resource_location: str):
        super().__init__(resource_location, "\n")

    def get_freqs_and_curve(self):
        d = self.ask(":CALCulate:DATA?")
        d = [float(f) for f in d.split(",")]
        d = np.array(d)
        x = d[::2]
        y = d[1::2]
        return x, y
