from typing import Literal, Optional, Tuple

import numpy as np

from ..visa_driver import VisaDriver

_FORMATS_TYPE = Literal["ASCii", "INT,32", "REAL,32", "REAL,64", "UINT,16"]


class AgilentSA(VisaDriver):
    """
    A driver for controlling Agilent Spectrum Analyzers via the VISA interface.

    This class provides methods to control and query Agilent Spectrum Analyzers, including setting and querying
    frequency span, center frequency, resolution bandwidth (RBW), video bandwidth (VBW), sweep time, and data format.
    It also includes methods to retrieve calculated data, trace data, and maximum point data.

    Usage
    -----
    ```
    from driverlib.agilent import AgilentSA

    agilent_sa = AgilentSA("TCPIP0::123.456.789.012::inst0::INSTR")

    freqs, data = agilent_sa.get_calc_data()
    ```

    Args:
        resource_location (str): The VISA resource name used to connect to the device.
    """

    def __init__(self, resource_location: str):
        """Initialize the AgilentSA object with the specified resource location.

        The constructor configures the communication termination character as a newline character.

        Args:
            resource_location (str): The VISA resource name used to connect to the device.
        """
        super().__init__(resource_location, "\n")

    def get_span(self) -> float:
        """Query the frequency span of the spectrum analyzer.

        Returns:
            float: The frequency span in Hz.
        """
        return float(self.ask(":FREQuency:SPAN?"))

    def set_span(self, value: float):
        """Set the frequency span of the spectrum analyzer.

        Args:
            value (float): The desired frequency span in Hz.
        """
        self.write(f":FREQuency:SPAN {value}")

    span = property(get_span, set_span)

    def get_center(self) -> float:
        """Query the center frequency of the spectrum analyzer.

        Returns:
            float: The center frequency in Hz.
        """
        return float(self.ask(":FREQuency:CENTer?"))

    def set_center(self, value: float):
        """Set the center frequency of the spectrum analyzer.

        Args:
            value (float): The desired center frequency in Hz.
        """
        self.write(f":FREQuency:CENTer {value}")

    center = property(get_center, set_center)

    def get_rbw(self) -> int:
        """Query the resolution bandwidth (RBW) of the spectrum analyzer.

        Returns:
            int: The RBW in Hz.
        """
        return int(float(self.ask(":BANDwidth:RESolution?")))

    def set_rbw(self, value: int):
        """Set the resolution bandwidth (RBW) of the spectrum analyzer.

        Args:
            value (int): The desired RBW in Hz.
        """
        self.write(f":BANDwidth:RESolution {int(value)}")

    rbw = property(get_rbw, set_rbw)

    def get_vbw(self) -> int:
        """Query the video bandwidth (VBW) of the spectrum analyzer.

        Returns:
            int: The VBW in Hz.
        """
        return int(float(self.ask(":BANDwidth:VIDeo?")))

    def set_vbw(self, value: int):
        """Set the video bandwidth (VBW) of the spectrum analyzer.

        Args:
            value (int): The desired VBW in Hz.
        """
        self.write(f":BANDwidth:VIDeo {int(value)}")

    vbw = property(get_vbw, set_vbw)

    def get_sweep_time(self) -> Optional[float]:
        """Query the sweep time of the spectrum analyzer.

        Returns:
            Optional[float]: The sweep time in seconds, or None if set to auto.
        """
        sweep_time = self.ask(":SENSe:SWEep:TIME?")
        if sweep_time.lower() == "auto":
            return None
        return float(sweep_time)

    def set_sweep_time(self, value: Optional[float]):
        """Set the sweep time of the spectrum analyzer.

        Args:
            value (Optional[float]): The desired sweep time in seconds, or None to set to auto.
        """
        if value is None:
            self.write(":SENSe:SWEep:TIME:AUTO ON")
        else:
            self.write(f":SENSe:SWEep:TIME {value}")  # time in seconds

    sweep_time = property(get_sweep_time, set_sweep_time)

    def get_data_format(self) -> _FORMATS_TYPE:
        """Query the data format for trace data from the spectrum analyzer.

        Returns:
            _FORMATS_TYPE: The current data format.
        """
        return self.ask(":FORMat:TRACe:DATA?")

    def set_data_format(self, value: _FORMATS_TYPE = "ASCii"):
        """Set the data format for trace data from the spectrum analyzer.

        Args:
            value (_FORMATS_TYPE): The desired data format.
        """
        self.write(f":FORMat:TRACe:DATA {value}")

    data_format = property(get_data_format, set_data_format)

    def get_calc_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Retrieve the calculated data from the spectrum analyzer.

        Returns:
            Tuple[np.ndarray, np.ndarray]: The frequencies and amplitude as np.arrays.
        """
        d = self.ask(":CALCulate:DATA?")
        d = [float(f) for f in d.split(",")]
        d = np.array(d)
        x = d[::2]
        y = d[1::2]
        return x, y

    def get_trace(self, trace: int = 1):
        """Retrieve the trace data for a specified trace number from the spectrum analyzer.

        Args:
            trace (int, optional): The trace number. Defaults to 1.

        Returns:
            np.ndarray: The trace data as a numpy array.
        """
        raw = self.ask(f":TRACe:DATA? TRACE{trace}")
        return np.asarray([float(f) for f in raw.split(",")])

    def get_freq_and_trace(
        self,
        trace: int = 1,
        center: Optional[float] = None,
        span: Optional[float] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Retrieves the trace data and corresponding frequency points from the spectrum analyzer.

        This method allows specifying a trace number, and optionally the center frequency and span
        to use for frequency calculations. If the center frequency and span are not provided,
        the current settings of the spectrum analyzer are used.

        Args:
            trace (int): The trace number to retrieve data from. Defaults to 1.
            center (Optional[float]): The center frequency in Hz. If None, the current center
                frequency of the spectrum analyzer is used. Defaults to None.
            span (Optional[float]): The frequency span in Hz. If None, the current span of the
                spectrum analyzer is used. Defaults to None.

        Returns:
            Tuple[np.ndarray, np.ndarray]: A tuple containing two numpy arrays. The first array
                contains the trace data points, and the second contains the corresponding
                frequency points in Hz.
        """
        # Get the current center frequency and span if not provided
        if span is None:
            span = self.get_span()
        if center is None:
            center = self.get_center()

        # Ensure the data format is set to ASCII.
        self.set_data_format("ASCii")

        # Retrieve the trace data from the specified trace number
        data = self.get_trace(trace=trace)

        # Calculate the frequency points corresponding to each data point in the trace
        freqs = np.linspace(center - span / 2, center + span / 2, len(data))

        return freqs, data

    def get_max_point(self, marker: int = 1) -> float:
        """Find the maximum point on the specified marker and returns its frequency.

        Args:
            marker (int, optional): The marker number. Defaults to 1.

        Returns:
            float: The frequency of the maximum point in Hz.
        """
        self.write(f":CALCulate:MARKer{marker}:MAXimum")
        return float(self.ask(f":CALCulate:MARKer{marker}:X?"))

    def set_trace_parameters_and_get(
        self, center: float, span: float, rbw: int = 100, vbw: int = 30, swt: Optional[float] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Configure and measure.

        This method sets the center frequency, span, resolution bandwidth (RBW), video bandwidth
            (VBW), and sweep time for the spectrum analyzer. It then retrieves the trace data
            displayed on the screen along with the corresponding frequency values.

        Args:
            center (float): Center frequency in Hz.
            span (float): Frequency span in Hz.
            rbw (int): Resolution bandwidth in Hz. Defaults to 100.
            vbw (int): Video bandwidth in Hz. Defaults to 30.
            swt (Optional[float]): Total sweep time in seconds. None for auto. Defaults to None.

        Returns:
            Tuple[np.ndarray, np.ndarray]: A tuple containing two numpy arrays. The first array
            contains the trace data, and the second contains the corresponding frequencies.
        """
        self.center = center
        self.span = span
        self.rbw = rbw
        self.vbw = vbw
        self.sweep_time = swt

        self.write(":DISPlay:WINdow:TRACe:Y:SCALe:SPACing LOGarithmic")

        return self.get_freq_and_trace(trace=1, span=span, center=center)
