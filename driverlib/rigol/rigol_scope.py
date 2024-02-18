# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 10:47:25 2021

@author: Tangui ALADJIDI
"""

# TODO: Should be refactored and checked!
# TODO: Methods should be extracted to a separate functions.
# TODO: Docstring should be rewritten in google styling.

import os
import sys
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from ..visa_driver import OpenResource, VisaDriver

_CHANNELS_TYPE = Optional[List[int]]


class _Preamble:
    def __init__(self, s):
        elems = s.split(",")
        self.elems = elems
        self.points = int(elems[2])
        self.count = int(elems[3])
        self.x_inc = float(elems[4])
        self.x_orig = float(elems[5])
        self.x_ref = float(elems[6])
        self.y_inc = float(elems[7])
        self.y_orig = int(elems[8])
        self.y_ref = int(elems[9])

    def normalize(self, raw_y):
        yvals = raw_y.astype(np.float64)
        yvals -= self.y_orig + self.y_ref
        yvals *= self.y_inc
        return yvals

    def x_values(self):
        xvals = np.linspace(0, self.points - 1, self.points)
        xvals *= self.x_inc
        xvals += self.x_ref
        # xvals += self.x_orig
        return xvals


class RigolScopeDriver(VisaDriver):
    def query_ascii_values(self, message):
        with OpenResource(self.rm, self.resource_location, self.endline) as driver:
            return driver.query_ascii_values(message)

    def query_binary_values(self, message, *args, **kwargs):
        with OpenResource(self.rm, self.resource_location, self.endline) as driver:
            return driver.query_binary_values(message, *args, **kwargs)

    def write_ascii_values(self, message, value):
        with OpenResource(self.rm, self.resource_location, self.endline) as driver:
            driver.write_ascii_values(message, value)


class RigolScope(RigolScopeDriver):
    def get_waveform_raw(
        self, channels: _CHANNELS_TYPE = None, plot: bool = False, memdepth: float = None
    ) -> np.ndarray:
        """
        Gets the waveform of a selection of channels
        :param list channels: List of channels
        :param bool plot: Will plot the traces
        :param float memdepth: Memory depth (number of points) defaults to
        None
        (does not modify)
        :returns: Data, Time np.ndarrays containing the traces of shape
        (channels, nbr of points) if len(channels)>1
        """
        if channels is None:
            channels = [1]
        Data = []
        Time = []
        if plot:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            leg = []
        if len(channels) > 4:
            print("ERROR : Invalid channel list provided" + " (List too long)")
            sys.exit()
        for chan in channels:
            if chan > 4:
                print("ERROR : Invalid channel list provided" + " (Channels are 1,2,3,4)")
                sys.exit()
        if memdepth is not None:
            self.write(f":ACQuire:MDEPth {int(memdepth)}")
        self.write(":STOP")
        # Select channels
        for chan in channels:
            self.write(f":WAV:SOUR CHAN{chan}")
            # Y origin for wav data
            YORigin = self.query_ascii_values(":WAV:YOR?")[0]
            # Y REF for wav data
            YREFerence = self.query_ascii_values(":WAV:YREF?")[0]
            # Y INC for wav data
            YINCrement = self.query_ascii_values(":WAV:YINC?")[0]

            # X REF for wav data
            XREFerence = self.query_ascii_values(":WAV:XREF?")[0]
            # X INC for wav data
            XINCrement = self.query_ascii_values(":WAV:XINC?")[0]
            memory_depth = int(self.query_ascii_values(":ACQuire:MDEPth?")[0])
            # Set the waveform reading mode to RAW.
            self.write(":WAV:MODE RAW")
            # Set return format to Byte.
            self.write(":WAV:FORM BYTE")
            # Set waveform read start to 0.
            self.write(":WAV:STAR 1")
            if memory_depth > 250000:
                # Set waveform read stop to 250000.
                self.write(":WAV:STOP 250000")
            else:
                self.write(f":WAV:STOP {int(memory_depth)}")
            # Read data from the resource, excluding the first 9 bytes
            # (TMC header).
            rawdata = self.query_binary_values(":WAV:DATA?", datatype="B")
            sys.stdout.write(f"\rReading {len(rawdata)}/{memory_depth}")
            # Check if memory depth is bigger than the first data extraction.
            if memory_depth > 250000:
                # Find the maximum number of loops required to loop through all
                # memory.
                loopmax = int(np.ceil(memory_depth / 250000))
                for loopcount in range(1, loopmax):
                    # Calculate the next start of the waveform in the internal
                    # memory.
                    start = (loopcount * 250000) + 1
                    self.write(f":WAV:STAR {start}")
                    # Calculate the next stop of the waveform in the internal
                    # memory
                    stop = (loopcount + 1) * 250000
                    sys.stdout.write(f"\rReading {stop}/{memory_depth}")
                    self.write(f":WAV:STOP {stop}")
                    # Extent the rawdata variables with the new values.
                    rawdata.extend(self.query_binary_values(":WAV:DATA?", datatype="B"))
            print()
            data = (np.asarray(rawdata) - YORigin - YREFerence) * YINCrement
            Data.append(data)
            # Calculate data size for generating time axis
            data_size = len(data)
            # Create time axis
            times = np.linspace(XREFerence, XINCrement * data_size, data_size)
            Time.append(times)
            if plot:
                leg.append(f"Channel {chan}")
                # See if we should use a different time axis
                if times[-1] < 1e-3:
                    times *= 1e6
                    tUnit = "uS"
                elif times[-1] < 1:
                    times *= 1e3
                    tUnit = "mS"
                else:
                    tUnit = "S"
                # Graph data with pyplot.
                ax.plot(times, data)
                ax.set_ylabel("Voltage (V)")
                ax.set_xlabel("Time (" + tUnit + ")")
                ax.set_xlim(times[0], times[-1])
        self.write(":RUN")
        if plot:
            ax.legend(leg)
            plt.show()
        Data = np.asarray(Data)
        Time = np.asarray(Time)
        if len(channels) == 1:
            Data = Data[0, :]
            Time = Time[0, :]
        return Data, Time

    def get_waveform(
        self,
        channels: _CHANNELS_TYPE = None,
        plot: bool = False,
        ndivs: int = 10,
    ) -> np.ndarray:
        """Retrieves the displayed waveform.
        From the displayed time scale and the sampling rate, will compute how many
        points of the memory correspond to the displayed signal.
        It will then retrieve the displayed signal (the part delimited by the
        shaded area on top of the screen).
        See the :WAVeform Commands documentation for futher details.

        Args:
            channels (list, optional): List of channels. Defaults to [1].
            plot (bool, optional): Whether to plot the result. Defaults to False.
            ndivs (int, optional): The number of time divisions on the screen.
              Defaults to 10.

        Returns:
            np.ndarray: Data, Time
        """
        if channels is None:
            channels = [1]
        Data = []
        Time = []
        memory_depth = int(self.query_ascii_values(":ACQuire:MDEPth?")[0])
        time_scale = float(self.query_ascii_values(":TIM:SCAL?")[0])
        if plot:
            fig, ax = plt.subplots()
        self.write(":STOP")
        for chan in channels:
            self.write(f":WAV:SOUR CHAN{chan}")
            self.write(":WAV:MODE MAX")
            self.write(":WAV:FORM BYTE")
            preamble = _Preamble(self.ask(":WAV:PRE?"))
            screen_points = np.floor(time_scale / preamble.x_inc) * ndivs
            # we look for the middle of the memory and take what's displayed
            # on the screen
            self.write(f"WAV:STAR {memory_depth//2 - screen_points//2+1}")
            self.write(f"WAV:STOP {memory_depth//2 + screen_points//2}")
            data = self.query_binary_values(
                ":WAV:DATA?", datatype="B", container=np.array, delay=0.5, data_points=screen_points
            )
            data = preamble.normalize(data)
            times = np.arange(0, len(data) * preamble.x_inc, preamble.x_inc)
            Data.append(data)
            Time.append(times)
            if plot:
                if times[-1] < 1e-3:
                    times *= 1e6
                    tUnit = "uS"
                elif times[-1] < 1:
                    times *= 1e3
                    tUnit = "mS"
                else:
                    tUnit = "S"
                ax.plot(times, data, label=f"Channel {chan}")
                ax.set_ylabel("Voltage (V)")
                ax.set_xlabel("Time (" + tUnit + ")")
                ax.set_xlim(times[0], times[-1])
        self.write(":RUN")
        if plot:
            ax.legend()
            plt.show()
        return np.asarray(Time), np.asarray(Data)

    def set_xref(self, ref: float):
        """
        Sets the x reference
        :param ref: Reference point
        :type ref: float
        :return: None
        :rtype: None

        """

        try:
            self.write_ascii_values(":WAV:XREF", ref)
        except (ValueError, TypeError, AttributeError):
            print("Improper value for XREF !")
        self.xref = self.query_ascii_values(":WAV:XREF?")[0]

    def set_yref(self, ref: float):
        try:
            self.write_ascii_values(":WAV:YREF", ref)
        except (ValueError, TypeError, AttributeError):
            print("Improper value for YREF !")
        self.xref = self.query_ascii_values(":WAV:YREF?")[0]

    def set_yres(self, res: float) -> float:
        self.write_ascii_values(":WAV:YINC", res)

    def set_xres(self, res: float) -> float:
        self.write_ascii_values(":WAV:XINC", res)

    def get_screenshot(
        self, filename: str = None, format_: str = "png", image_size: Tuple[int, int] = (600, 1024)
    ):
        """
        Recovers a screenshot of the screen and returns the image
        :param filename: Location where the image will be saved
        :param format: Image format in ['jpg', 'png', 'tiff','bmp8', 'bmp24']
        """
        assert format_ in ("jpeg", "png", "bmp8", "bmp24", "tiff")
        raw_img = self.write_and_read(f":disp:data? on,off,{format_}", timeout=60_000)

        img = np.asarray(raw_img).reshape(image_size)
        if not filename:
            return img

        try:
            os.remove(filename)
        except OSError:
            pass
        with open(filename, "wb") as fs:
            fs.write(raw_img)

    def close(self):
        self.write(":RUN")
        super().close()
