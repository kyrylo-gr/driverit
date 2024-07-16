import numpy as np

from ..visa_driver import VisaDriver

# quick and dirty for now, waiting for answers to the question :
# http://stackoverflow.com/questions/13840997/python-instrument-drivers


class AFG(VisaDriver):

    _supported_models = ["AFG3102", "AFG3022B"]

    def __init__(self, resource_location: str, model_name: str):
        del model_name
        super().__init__(resource_location)

        self.channel_idx = 1
        # self.amplitudelock = False
        # self.frequencylock = False
        # self.phaseinit()

    def recall(self, num: str = "1") -> None:
        self.write(f"*RCL {num}")

    def save(self, num: str = "1") -> None:
        self.write(f"*SAV {num}")

    @property
    def output_enabled(self) -> bool:
        return self.ask(f"OUTPut{self.channel_idx}:STATe?") == "1"

    @output_enabled.setter
    def output_enabled(self, val: bool) -> None:
        if val:
            self.write(f"OUTPut{self.channel_idx}:STATe ON")
        else:
            self.write(f"OUTPut{self.channel_idx}:STATe OFF")

    @property
    def am(self) -> bool:
        return self.ask(f"SOURCe{self.channel_idx}:AM:STATe?") == "1"

    @am.setter
    def am(self, val: bool) -> None:
        if val:
            self.write(f"SOURCe{self.channel_idx}:AM:STATe ON")
        else:
            self.write(f"SOURCe{self.channel_idx}:AM:STATe OFF")

    @property
    def fm(self) -> bool:
        return self.ask(f"SOURCe{self.channel_idx}:FM:STATe?") == "1"

    @fm.setter
    def fm(self, val: bool) -> None:
        if val:
            self.write(f"SOURCe{self.channel_idx}:FM:STATe ON")
        else:
            self.write(f"SOURCe{self.channel_idx}:FM:STATe OFF")

    @property
    def pm(self) -> bool:
        return self.ask(f"SOURCe{self.channel_idx}:PM:STATe?") == "1"

    @pm.setter
    def pm(self, val: bool) -> None:
        if val:
            self.write(f"SOURCe{self.channel_idx}:PM:STATe ON")
        else:
            self.write(f"SOURCe{self.channel_idx}:PM:STATe OFF")

    @property
    def pwm(self) -> bool:
        return self.ask(f"SOURCe{self.channel_idx}:PWM:STATe?") == "1"

    @pwm.setter
    def pwm(self, val: bool) -> None:
        if val:
            self.write(f"SOURCe{self.channel_idx}:PWM:STATe ON")
        else:
            self.write(f"SOURCe{self.channel_idx}:PWM:STATe OFF")

    def calibrate(self) -> bool:
        return int(self.ask("*CAL?")) == 0

    def phaseinit(self) -> None:
        self.write(f"SOURce{self.channel_idx}:PHASe:INITiate")

    @property
    def waveform(self) -> str:
        return self.ask(f"SOURce{self.channel_idx}:FUNCtion:SHAPe?")

    @waveform.setter
    def waveform(self, val: str = "SIN") -> None:
        self.write(f"SOURce{self.channel_idx}:FUNCtion:SHAPe {val}")

    @property
    def duty_cycle_high(self) -> float:
        return float(self.ask(f"SOURce{self.channel_idx}:FUNCtion:RAMP:SYMMetry?"))

    @duty_cycle_high.setter
    def duty_cycle_high(self, val: float = 50.0) -> None:
        self.write(f"SOURce{self.channel_idx}:FUNCtion:RAMP:SYMMetry {val: f}")

    @property
    def impedance(self) -> float:
        return float(self.ask(f"OUTPut{self.channel_idx}:IMPedance?"))

    @impedance.setter
    def impedance(self, val=50) -> None:
        self.write(f"OUTPut{self.channel_idx}:IMPedance {val:f}OHM")

    @property
    def polarity(self) -> str:
        return self.ask(f"OUTPut{self.channel_idx}:POLarity?")

    @polarity.setter
    def polarity(self, val: str = "NORMal") -> None:
        self.write(f"OUTPut{self.channel_idx}:POLarity {val}")

    @property
    def triggerout(self) -> str:
        return self.ask("OUTPut:TRIGger:MODE?")

    @triggerout.setter
    def triggerout(self, val: str = "TRIGger") -> None:
        self.write(f"OUTPut:TRIGger:MODE {val}")

    @property
    def roscillator(self) -> str:
        return self.ask("SOURce:ROSCillator:SOURce?")

    @roscillator.setter
    def roscillator(self, val: str = "EXT") -> None:
        self.write(f"SOURce:ROSCillator:SOURce {val}")

    @property
    def amplitudelock(self) -> bool:
        """check if the voltages of both channels locked to each other"""
        return self.ask(f"SOURCe{self.channel_idx}:VOLTage:CONCurrent:STATe?") == "1"

    @amplitudelock.setter
    def amplitudelock(self, val: bool) -> None:
        """locks voltages of both channels to each other"""
        if val:
            self.write(f"SOURCe{self.channel_idx}:VOLTage:CONCurrent:STATe ON")
        else:
            self.write(f"SOURCe{self.channel_idx}:VOLTage:CONCurrent:STATe OFF")

    @property
    def frequencylock(self) -> bool:
        """checks if frequencies of both channels locked to each other"""
        return self.ask(f"SOURCe{self.channel_idx}:FREQuency:CONCurrent:STATe?") == "1"

    @frequencylock.setter
    def frequencylock(self, val) -> None:
        """locks frequencies of both channels to each other"""
        if val:
            self.write(f"SOURCe{self.channel_idx}:FREQuency:CONCurrent:STATe ON")
        else:
            self.write(f"SOURCe{self.channel_idx}:FREQuency:CONCurrent:STATe OFF")

    # numerical values
    @property
    def amplitude(self) -> float:
        """Get the signal amplitude in Vpp"""
        return float(
            self.ask(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:AMPLitude?")
        )

    @amplitude.setter
    def amplitude(self, val: float = 0) -> None:
        """Defines the signal amplitude in Vpp"""
        self.write(
            f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:AMPLitude {val:f}VPP"
        )

    @property
    def frequency(self) -> float:
        """Get frequency"""
        return float(self.ask(f"SOURCe{self.channel_idx}:FREQuency:FIXed?"))

    @frequency.setter
    def frequency(self, val: float = 0) -> None:
        """Update frequency"""
        self.write(f"SOURCe{self.channel_idx}:FREQuency:FIXed {val:f}Hz")

    @property
    def phase(self) -> float:
        """Get phase in degrees"""
        return (
            180.0 / np.pi * float(self.ask(f"SOURce{self.channel_idx}:PHASe:ADJust?"))
        )

    @phase.setter
    def phase(self, val: float = 0) -> None:
        """Set phase in degrees"""
        val = val % 360.0
        while val > 180.0:
            val -= 360.0
        self.write(f"SOURce{self.channel_idx}:PHASe:ADJust {val:.2f} DEG")

    @property
    def offset(self) -> float:
        """Get the offset"""
        return float(
            self.ask(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:OFFSet?")
        )

    @offset.setter
    def offset(self, val: float = 0) -> None:
        """Set the offset"""
        self.write(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:OFFSet {val:f}V")

    @property
    def high(self) -> float:
        """Get the high value for voltage"""
        return float(
            self.ask(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:HIGH?")
        )

    @high.setter
    def high(self, val: float = 0) -> None:
        """Set the high value for voltage"""
        self.write(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:HIGH {val:f}V")

    @property
    def low(self) -> float:
        """Get the low value for voltage"""
        return float(self.ask(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:LOW?"))

    @low.setter
    def low(self, val: float = 0) -> None:
        """Set the low value for voltage"""
        self.write(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:LOW {val:f}V")

    @property
    def triggersource(self) -> str:
        return self.ask("TRIGger:SEQuence:SOURce?")

    @triggersource.setter
    def triggersource(self, val: str = "TIM") -> None:
        self.write(f"TRIGger:SEQuence:SOURce {val}")

    @property
    def triggerslope(self) -> str:
        return self.ask("TRIGger:SEQuence:SLOPe?")

    @triggerslope.setter
    def triggerslope(self, val: str = "POS") -> None:
        self.write(f"TRIGger:SEQuence:SLOPe {val}")

    @property
    def triggertimer(self) -> float:
        return float(self.ask("TRIGger:SEQuence:TIMer?"))

    @triggertimer.setter
    def triggertimer(self, val: float = 1) -> None:
        self.write(f"TRIGger:SEQuence:TIMer {val}s")

    def trigger(self) -> None:
        """Triggers the measurement"""
        self.write("TRIGger:SEQuence:IMMediate")

    @property
    def burstenabled(self) -> bool:
        return self.ask(f"SOURce{self.channel_idx}:BURst:STATe?") == "1"

    @burstenabled.setter
    def burstenabled(self, val: bool = False) -> None:
        if val:
            self.write(f"SOURce{self.channel_idx}:BURst:STATe ON")
        else:
            self.write(f"SOURce{self.channel_idx}:BURst:STATe OFF")

    @property
    def burstcycles(self) -> int:
        return int(self.ask(f"SOURce{self.channel_idx}:BURst:NCYCles?"))

    @burstcycles.setter
    def burstcycles(self, val: int = 1) -> None:
        self.write(f"SOURce{self.channel_idx}:BURst:NCYCles {val}")

    @property
    def burstdelay(self) -> float:
        return float(self.ask(f"SOURce{self.channel_idx}:BURst:TDelay?"))

    @burstdelay.setter
    def burstdelay(self, val: float = 0.0) -> None:
        self.write(f"SOURce{self.channel_idx}:BURst:TDelay {val:f}s")

    @property
    def burstmode(self) -> str:
        return self.ask(f"SOURce{self.channel_idx}:BURst:MODE?")

    @burstmode.setter
    def burstmode(self, val: str = "TRIG") -> None:
        self.write(f"SOURce{self.channel_idx}:BURst:MODE {val}")

    @property
    def output_mode(self):
        return self.ask(f"SOURce{self.channel_idx}:FREQuency:MODE?")

    def get_continuous(self):
        ans = self.ask(f"SOURce{self.channel_idx}:FREQuency:MODE?")
        if ans == "CW":
            return 1
        else:
            return 0

    def set_continuous(self, val: bool = True) -> None:
        if val == False:
            raise Exception(
                "mode can't be turned off, only changed. Call the function for a new mode if that's what you need."
            )
        self.write(f"SOURce{self.channel_idx}:FREQuency:MODE CW")

    continuous = property(get_continuous, set_continuous)

    def get_sweep_mode(self):
        ans = self.ask(f"SOURce{self.channel_idx}:FREQuency:MODE?")
        if ans == "SWE":
            return 1
        else:
            return 0

    def set_sweep_mode(self, val: bool = True) -> None:
        if val == False:
            raise Exception(
                "mode can't be turned off, only changed. Call the function for a new mode if that's what you need."
            )
        self.write(f"SOURce{self.channel_idx}:FREQuency:MODE SWE")

    sweep_mode = property(get_sweep_mode, set_sweep_mode)

    def get_sweep_center(self):
        return float(self.ask(f"SOURce{self.channel_idx}:FREQuency:CENTer?"))

    def set_sweep_center(self, val: float):
        self.write(f"SOURce{self.channel_idx}:FREQuency:CENTer {val:f}Hz")

    sweep_center = property(get_sweep_center, set_sweep_center)

    def get_sweep_span(self):
        return float(self.ask(f"SOURce{self.channel_idx}:FREQuency:SPAN?"))

    def set_sweep_span(self, val: float):
        self.write(f"SOURce{self.channel_idx}:FREQuency:SPAN {val:f}Hz")

    sweep_span = property(get_sweep_span, set_sweep_span)

    def get_sweep_spacing(self):
        return self.ask(f"SOURce{self.channel_idx}:SWEep:SPACing?")

    def set_sweep_spacing(self, val: str = "LIN"):
        self.write(f"SOURce{self.channel_idx}:SWEep:SPACing {val}")

    sweep_spacing = property(get_sweep_spacing, set_sweep_spacing)

    def get_sweep_rtime(self):
        return float(self.ask(f"SOURce{self.channel_idx}:SWEep:RTIMe?"))

    def set_sweep_rtime(self, val: float = 1e-3):
        self.write(f"SOURce{self.channel_idx}:SWEep:RTIMe {val:f} s")

    sweep_rtime = property(get_sweep_rtime, set_sweep_rtime)

    def get_sweep_time(self):
        return float(self.ask(f"SOURce{self.channel_idx}:SWEep:TIME?"))

    def set_sweep_time(self, val: float = 1e-3):
        assert val >= 1e-3 and val <= 300
        self.write(f"SOURce{self.channel_idx}:SWEep:TIME {val:f} s")

    sweep_time = property(get_sweep_time, set_sweep_time)


#
# """ BLANK to fill in new properties
#    @property
#    def (self):
#        return float(self.ask("%d?"%self.channel_idx))
#    @.setter
#    def (self,val=0):
#        self.write("%d"%self.channel_idx%val)
#

# """
