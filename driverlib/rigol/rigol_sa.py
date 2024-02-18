# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 10:47:25 2021

@author: Tangui ALADJIDI
"""
# TODO: method should be extracted to a separate functions.
# TODO: docstring should be rewritten in google styling.

import numpy as np

from ..visa_driver import VisaDriver


class RigolSA(VisaDriver):

    def zero_span(
        self,
        center: float = 1e6,
        rbw: int = 100,
        vbw: int = 30,
        swt: float = "auto",
        trig: bool = None,
    ):
        """Zero span measurement.
        :param float center: Center frequency in Hz, converted to int
        :param float rbw: Resolution bandwidth
        :param float vbw: Video bandwidth
        :param float swt: Total measurement time. Except if set to 'auto'
        :param bool trig: External trigger
        :return: data, time for data and time
        :rtype: np.ndarray

        """
        self.write(":FREQuency:SPAN 0")
        self.write(f":FREQuency:CENTer {center}")
        self.write(f":BANDwidth:RESolution {int(rbw)}")
        self.write(f":BANDwidth:VIDeo {int(vbw)}")
        if swt != "auto":
            self.write(f":SENSe:SWEep:TIME {swt}")  # in s.
        else:
            self.write(":SENSe:SWEep:TIME:AUTO ON")
        self.write(":DISPlay:WINdow:TRACe:Y:SCALe:SPACing LOGarithmic")
        # self.write(':POWer:ASCale')
        if trig is not None:
            trigstate = self.ask(":TRIGger:SEQuence:SOURce?")
            istrigged = trigstate != "IMM"
            if trig and not (istrigged):
                self.write(":TRIGger:SEQuence:SOURce EXTernal")
                self.write(":TRIGger:SEQuence:EXTernal:SLOPe POSitive")
            elif not (trig) and istrigged:
                self.write(":TRIGger:SEQuence:SOURce IMMediate")
        self.write(":CONFigure:ACPower")
        self.write(":TPOWer:LLIMit 0")
        self.write(f":TPOWer:RLIMit {swt}")
        self.write(":FORMat:TRACe:DATA ASCii")
        # if specAn was trigged before, put it back in the same state
        if trig is not None and not (trig) and istrigged:
            self.write(f":TRIGger:SEQuence:SOURce {trigstate}")
        data = self.query_data()
        sweeptime = float(self.ask(":SWEep:TIME?"))
        times = np.linspace(0, sweeptime, len(data))
        return data, times

    def span(
        self,
        center: float = 22.5e6,
        span: float = 45e6,
        rbw: int = 100,
        vbw: int = 30,
        swt: float = "auto",
        trig: bool = None,
    ):
        """Arbitrary span measurement.
        :param float center: Center frequency in Hz
        :param float span: span
        :param float rbw: Resolution bandwidth
        :param float vbw: Video bandwidth
        :param float swt: Total measurement time
        :param bool trig: External trigger
        :return: data, freqs for data and frequencies
        :rtype: np.ndarray

        """
        self.write(f":FREQuency:SPAN {span}")
        self.write(f":FREQuency:CENTer {center}")
        self.write(f":BANDwidth:RESolution {int(rbw)}")
        self.write(f":BANDwidth:VIDeo {int(vbw)}")
        if swt != "auto":
            self.write(f":SENSe:SWEep:TIME {swt}")  # in s.
        else:
            self.write(":SENSe:SWEep:TIME:AUTO ON")
        self.write(":DISPlay:WINdow:TRACe:Y:SCALe:SPACing LOGarithmic")
        # self.write(':POWer:ASCale')
        if trig is not None:
            trigstate = self.ask(":TRIGger:SEQuence:SOURce?")
            istrigged = trigstate != "IMM"
            if trig and not (istrigged):
                self.write(":TRIGger:SEQuence:SOURce EXTernal")
                self.write(":TRIGger:SEQuence:EXTernal:SLOPe POSitive")
            elif not (trig) and istrigged:
                self.write(":TRIGger:SEQuence:SOURce IMMediate")
        self.write(":CONFigure:ACPower")
        self.write(":FORMat:TRACe:DATA ASCii")
        # if specAn was trigged before, put it back in the same state
        if trig is not None and not (trig) and istrigged:
            self.write(f":TRIGger:SEQuence:SOURce {trigstate}")
        data = self.query_data()
        # sweeptime = float(self.ask(':SWEep:TIME?'))
        freqs = np.linspace(center - span // 2, center + span // 2, len(data))
        return data, freqs

    def query_data(self):
        """Lower level function to grab the data from the SpecAnalyzer

        :return: data
        :rtype: list

        """
        self.write(":INITiate:PAUSe")
        rawdata = self.ask(":TRACe? TRACE1")
        data = rawdata.split(", ")[1:]
        data = [float(i) for i in data]
        self.write(":TRACe:AVERage:CLEar")
        self.write(":INITiate:RESume")
        return np.asarray(data)
