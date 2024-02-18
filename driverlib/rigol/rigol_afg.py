# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 10:47:25 2021

@author: Tangui ALADJIDI
"""

# TODO: method should be extracted to a separate functions.
# TODO: docstring should be rewritten in google styling.

from ..visa_driver import VisaDriver


class RigolAFG(VisaDriver):

    def get_waveform(self, output: int = 1) -> list:
        """Get the waveform type as well as its specs.

        :param int output: Description of parameter `output`.
        :return: List containing all the parameters
        :rtype: list

        """
        if output not in [1, 2]:
            print("ERROR : Invalid output specified")
            return None
        ison = self.ask(f"OUTPut{output}?")[:-1] == "ON"
        ret = self.ask(f"SOURce{output}:APPLy?")
        ret = ret[1:-2].split(",")
        type_ = ret[0]
        freq = float(ret[1])
        amp = float(ret[2])
        offset = float(ret[3])
        phase = float(ret[4])
        return [ison, type_, freq, amp, offset, phase]

    def turn_on(self, output: int = 1):
        """Turn on an output channel on the last preset.
        :param int output: Output channel
        :return: None
        """
        self.write(f"OUTPut{output} ON")

    def turn_off(self, output: int = 1):
        """Turn off an output channel on the last preset.
        :param int output: Output channel
        :return: None
        """
        self.write(f"OUTPut{output} OFF")

    def set_impedance(self, output: int = 1, load: str = "INF"):
        """Set the output impedance to specified value.

        It doesn't actually change the physical impendance of the instrument, but changes the
        displayed voltage to match the actual voltage on the device under test.

        :param int output: Output channel
        :param str load: specified impedance value. {<ohms>|INFinity|MINimum|MAXimum}
        :return: None
        """
        if output not in [1, 2]:
            print("ERROR : Invalid output specified")
            return None
        self.write(f":OUTP{output}:IMP " + load)
        print(f"Impedance OUTP{output} set to :", self.ask(f":OUTP{output}:IMP?"))

    def dc_offset(self, output: int = 1, offset: float = 2.0):
        """Apply a constant voltage on the specified output.

        :param int output: Output channel
        :param float offset: Voltage applied in Volts
        :return: None
        """
        if output not in [1, 2]:
            print("ERROR : Invalid output specified")
            return None
        self.write(f":SOURce{output}:FUNCtion DC")
        self.write(f":SOURce{output}:APPLy:USER 1, 1, {offset}, 0")
        self.turn_on(output)

    def sine(
        self,
        output: int = 1,
        freq: float = 100.0,
        ampl: float = 2.0,
        offset: float = 0.0,
        phase: float = 0.0,
    ):
        """Set a sine wave on specified output.

        :param int output: Output channel
        :param float freq: Frequency of the signa in Hz
        :param float ampl: Amplitude of the wave in Volts
        :param float offset: Voltage offset in Volts
        :param float phase: Signal phase in degree
        :return: None
        """
        if output not in [1, 2]:
            print("ERROR : Invalid output specified")
            return None
        self.write(f":SOURce{output}:APPLy:SINusoid {freq}, {ampl}, " + f"{offset}, {phase}")
        self.turn_on(output)

    def square(
        self,
        output: int = 1,
        freq: float = 100.0,
        ampl: float = 2.0,
        offset: float = 0.0,
        phase: float = 0.0,
        duty: float = 50.0,
    ):
        """Set a square wave on specified output.

        :param int output: Output channel
        :param float freq: Frequency of the signa in Hz
        :param float ampl: Amplitude of the wave in Volts
        :param float offset: Voltage offset in Volts
        :param float phase: Signal phase in degree
        :param float duty: Duty cycle in percent
        :return: None
        """
        if output not in [1, 2]:
            print("ERROR : Invalid output specified")
            return None
        self.write(f":SOURce{output}:APPLy:SQUare {freq}, {ampl}, " + f"{offset}, {phase}")
        self.write(f":SOURce{output}:FUNCtion:SQUare:DCYCle {duty}")
        self.turn_on(output)

    def ramp(
        self,
        output: int = 1,
        freq: float = 100.0,
        ampl: float = 2.0,
        offset: float = 0.0,
        phase: float = 0.0,
        symm: float = 50.0,
    ):
        """Set a triangular wave on specified output.

        :param int output: Output channel
        :param float freq: Frequency of the signa in Hz
        :param float ampl: Amplitude of the wave in Volts
        :param float offset: Voltage offset in Volts
        :param float phase: Signal phase in degree
        :param float symm: Symmetry factor in percent (equivalent to duty)
        :return: None
        """
        if output not in [1, 2]:
            print("ERROR : Invalid output specified")
            return None
        self.write(f":SOURce{output}:APPLy:RAMP {freq}, {ampl}, " + f"{offset}, {phase}")
        self.write(f":SOURce{output}:FUNCtion:RAMP:SYMMetry {symm}")
        self.turn_on(output)

    def pulse(
        self,
        output: int = 1,
        freq: float = 100.0,
        ampl: float = 2.0,
        offset: float = 0.0,
        phase: float = 0.0,
        duty: float = 50.0,
        rise: float = 10e-9,
        fall: float = 10e-9,
    ):
        """Set a triangular wave on specified output.

        :param int output: Output channel
        :param float freq: Frequency of the signa in Hz
        :param float ampl: Amplitude of the wave in Volts
        :param float offset: Voltage offset in Volts
        :param float phase: Signal phase in degree
        :param float duty: Duty cycle in percent
        :param float rise: Rise time in seconds
        :param float fall: Fall time in seconds
        :return: None
        """
        if output not in [1, 2]:
            print("ERROR : Invalid output specified")
            return None
        self.write(f":SOURce{output}:APPLy:PULSe {freq}, {ampl}, " + f"{offset}, {phase}")
        self.write(f":SOURce{output}:FUNCtion:PULSe:DCYCLe {duty}")
        self.write(f":SOURce{output}:FUNCtion:TRANsition:LEADing {rise}")
        self.write(f":SOURce{output}:FUNCtion:TRANsition:TRAiling {fall}")
        self.turn_on(output)

    def noise(self, output: int = 1, ampl: float = 5.0, offset: float = 0.0):
        """Send noise on specified output.

        :param int output: Output channel
        :param float ampl: Amplitude in Volts
        :param float offset: Voltage offset in Volts
        :return: None
        """
        self.write(f":SOURce{output}:APPLy:NOISe {ampl}, {offset}")
        self.turn_on(output)

    def arbitrary(
        self,
        output: int = 1,
        freq: float = 100,
        ampl: float = 5.0,
        offset: float = 0.0,
        phase: float = 0.0,
        function: str = "SINC",
    ):
        """
        Arbitrary function signal.

        :param int output: Output channel
        :param float freq: Frequency of the signa in Hz
        :param float ampl: Amplitude of the wave in Volts
        :param float offset: Voltage offset
        :param float phase: Signal phase in degree
        :param str function: Function type
        :return: Description of returned object.
        :rtype: type

        """
        # List of all possible functions
        funcnames = [
            "KAISER",
            "ROUNDPM",
            "SINC",
            "NEGRAMP",
            "ATTALT",
            "AMPALT",
            "STAIRDN",
            "STAIRUP",
            "STAIRUD",
            "CPULSE",
            "NPULSE",
            "TRAPEZIA",
            "ROUNDHALF",
            "ABSSINE",
            "ABSSINEHALF",
            "SINETRA",
            "SINEVER",
            "EXPRISE",
            "EXPFALL",
            "TAN",
            "COT",
            "SQRT",
            "X2DATA",
            "GAUSS",
            "HAVERSINE",
            "LORENTZ",
            "DIRICHLET",
            "GAUSSPULSE",
            "AIRY",
            "CARDIAC",
            "QUAKE",
            "GAMMA",
            "VOICE",
            "TV",
            "COMBIN",
            "BANDLIMITED",
            "STEPRESP",
            "BUTTERWORTH",
            "CHEBYSHEV1",
            "CHEBYSHEV2",
            "BOXCAR",
            "BARLETT",
            "TRIANG",
            "BLACKMAN",
            "HAMMING",
            "HANNING",
            "DUALTONE",
            "ACOS",
            "ACOSH",
            "ACOTCON",
            "ACOTPRO",
            "ACOTHCON",
            "ACOTHPRO",
            "ACSCCON",
            "ACSCPRO",
            "ACSCHCON",
            "ACSCHPRO",
            "ASECCON",
            "ASECPRO",
            "ASECH",
            "ASIN",
            "ASINH",
            "ATAN",
            "ATANH",
            "BESSELJ",
            "BESSELY",
            "CAUCHY",
            "COSH",
            "COSINT",
            "COTHCON",
            "COTHPRO",
            "CSCCON",
            "CSCPRO",
            "CSCHCON",
            "CSCHPRO",
            "CUBIC,",
            "ERF",
            "ERFC",
            "ERFCINV",
            "ERFINV",
            "LAGUERRE",
            "LAPLACE",
            "LEGEND",
            "LOG",
            "LOGNORMAL",
            "MAXWELL",
            "RAYLEIGH",
            "RECIPCON",
            "RECIPPRO",
            "SECCON",
            "SECPRO",
            "SECH",
            "SINH",
            "SININT",
            "TANH",
            "VERSIERA",
            "WEIBULL",
            "BARTHANN",
            "BLACKMANH",
            "BOHMANWIN",
            "CHEBWIN",
            "FLATTOPWIN",
            "NUTTALLWIN",
            "PARZENWIN",
            "TAYLORWIN",
            "TUKEYWIN",
            "CWPUSLE",
            "LFPULSE",
            "LFMPULSE",
            "EOG",
            "EEG",
            "EMG",
            "PULSILOGRAM",
            "TENS1",
            "TENS2",
            "TENS3",
            "SURGE",
            "DAMPEDOSC",
            "SWINGOSC",
            "RADAR",
            "THREEAM",
            "THREEFM",
            "THREEPM",
            "THREEPWM",
            "THREEPFM",
            "RESSPEED",
            "MCNOSIE",
            "PAHCUR",
            "RIPPLE",
            "ISO76372TP1",
            "ISO76372TP2A",
            "ISO76372TP2B",
            "ISO76372TP3A",
            "ISO76372TP3B",
            "ISO76372TP4",
            "ISO76372TP5A",
            "ISO76372TP5B",
            "ISO167502SP",
            "ISO167502VR",
            "SCR",
            "IGNITION",
            "NIMHDISCHARGE",
            "GATEVIBR",
            "PPULSE",
        ]
        if function not in funcnames:
            print("ERROR : Unknwown function specified")
        self.write(f":SOURce{output}:FUNCtion {function}")
        self.write(f":SOURce{output}:APPLy:USER {freq}, {ampl}, " + f"{offset}, {phase}")
        self.turn_on(output)
