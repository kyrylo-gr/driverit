import numpy as np

from ..types import ONOFF_TYPE
from ..visa_driver import VisaDriver


class TektronixAFG(VisaDriver):
    """
    A class representing a Tektronix Arbitrary Function Generator (AFG).
    """

    _supported_models = ["AFG3102", "AFG3022B"]

    def __init__(self, resource_location: str, model_name: str):
        """
        Initialize the AFG object.

        Args:
            resource_location (str): The resource location of the AFG.
            model_name (str): The model name of the AFG.
        """
        del model_name
        super().__init__(resource_location)

        self._allow_attrs = self._allow_attrs + ["channel_idx"]

        self.channel_idx = 1
        # self.amplitudelock = False
        # self.frequencylock = False
        # self.phaseinit()

    def recall(self, num: str = "1") -> None:
        """
        Recall a saved configuration on the AFG.

        Args:
            num (str, optional): The number of the saved configuration. Defaults to "1".
        """
        self.write(f"*RCL {num}")

    def save(self, num: str = "1") -> None:
        """
        Save the current configuration on the AFG.

        Args:
            num (str, optional): The number to save the configuration as. Defaults to "1".
        """
        self.write(f"*SAV {num}")

    @property
    def output_enabled(self) -> bool:
        """
        Get the output state of the AFG.

        Returns:
            bool: The output state of the AFG.
        """
        return self.ask(f"OUTPut{self.channel_idx}:STATe?") == "1"

    @output_enabled.setter
    def output_enabled(self, val: bool) -> None:
        """
        Set the output state of the AFG.

        Args:
            val (bool): The output state to set.
        """
        if val:
            self.write(f"OUTPut{self.channel_idx}:STATe ON")
        else:
            self.write(f"OUTPut{self.channel_idx}:STATe OFF")

    @property
    def am(self) -> bool:
        """
        Get the amplitude modulation state of the AFG.

        Returns:
            bool: The amplitude modulation state of the AFG.
        """
        return self.ask(f"SOURCe{self.channel_idx}:AM:STATe?") == "1"

    @am.setter
    def am(self, val: bool) -> None:
        """
        Set the amplitude modulation state of the AFG.

        Args:
            val (bool): The amplitude modulation state to set.
        """
        if val:
            self.write(f"SOURCe{self.channel_idx}:AM:STATe ON")
        else:
            self.write(f"SOURCe{self.channel_idx}:AM:STATe OFF")

    @property
    def fm(self) -> bool:
        """
        Get the frequency modulation state of the AFG.

        Returns:
            bool: The frequency modulation state of the AFG.
        """
        return self.ask(f"SOURCe{self.channel_idx}:FM:STATe?") == "1"

    @fm.setter
    def fm(self, val: bool) -> None:
        """
        Set the frequency modulation state of the AFG.

        Args:
            val (bool): The frequency modulation state to set.
        """
        if val:
            self.write(f"SOURCe{self.channel_idx}:FM:STATe ON")
        else:
            self.write(f"SOURCe{self.channel_idx}:FM:STATe OFF")

    @property
    def pm(self) -> bool:
        """
        Get the phase modulation state of the AFG.

        Returns:
            bool: The phase modulation state of the AFG.
        """
        return self.ask(f"SOURCe{self.channel_idx}:PM:STATe?") == "1"

    @pm.setter
    def pm(self, val: bool) -> None:
        """
        Set the phase modulation state of the AFG.

        Args:
            val (bool): The phase modulation state to set.
        """
        if val:
            self.write(f"SOURCe{self.channel_idx}:PM:STATe ON")
        else:
            self.write(f"SOURCe{self.channel_idx}:PM:STATe OFF")

    @property
    def pwm(self) -> bool:
        """
        Get the pulse width modulation state of the AFG.

        Returns:
            bool: The pulse width modulation state of the AFG.
        """
        return self.ask(f"SOURCe{self.channel_idx}:PWM:STATe?") == "1"

    @pwm.setter
    def pwm(self, val: bool) -> None:
        """
        Set the pulse width modulation state of the AFG.

        Args:
            val (bool): The pulse width modulation state to set.
        """
        if val:
            self.write(f"SOURCe{self.channel_idx}:PWM:STATe ON")
        else:
            self.write(f"SOURCe{self.channel_idx}:PWM:STATe OFF")

    def calibrate(self) -> bool:
        """
        Perform calibration on the AFG.

        Returns:
            bool: True if calibration is successful, False otherwise.
        """
        return int(self.ask("*CAL?")) == 0

    def phase_initiate(self) -> None:
        """
        Initialize the phase of the AFG.
        """
        self.write(f"SOURce{self.channel_idx}:PHASe:INITiate")

    @property
    def waveform(self) -> str:
        """
        Get the waveform shape of the AFG.

        Returns:
            str: The waveform shape of the AFG.
        """
        return self.ask(f"SOURce{self.channel_idx}:FUNCtion:SHAPe?")

    @waveform.setter
    def waveform(self, val: str = "SIN") -> None:
        """
        Set the waveform shape of the AFG.

        Args:
            val (str, optional): The waveform shape to set. Defaults to "SIN".
        """
        self.write(f"SOURce{self.channel_idx}:FUNCtion:SHAPe {val}")

    @property
    def duty_cycle_high(self) -> float:
        """
        Get the duty cycle high value of the AFG.

        Returns:
            float: The duty cycle high value of the AFG.
        """
        return float(self.ask(f"SOURce{self.channel_idx}:FUNCtion:RAMP:SYMMetry?"))

    @duty_cycle_high.setter
    def duty_cycle_high(self, val: float = 50.0) -> None:
        """
        Set the duty cycle high value of the AFG.

        Args:
            val (float, optional): The duty cycle high value to set. Defaults to 50.0.
        """
        self.write(f"SOURce{self.channel_idx}:FUNCtion:RAMP:SYMMetry {val: f}")

    @property
    def impedance(self) -> float:
        """
        Get the output impedance of the AFG.

        Returns:
            float: The output impedance of the AFG.
        """
        return float(self.ask(f"OUTPut{self.channel_idx}:IMPedance?"))

    @impedance.setter
    def impedance(self, val=50) -> None:
        """
        Set the output impedance of the AFG.

        Args:
            val (float, optional): The output impedance to set. Defaults to 50.
        """
        self.write(f"OUTPut{self.channel_idx}:IMPedance {val:f}OHM")

    @property
    def polarity(self) -> str:
        """
        Get the output polarity of the AFG.

        Returns:
            str: The output polarity of the AFG.
        """
        return self.ask(f"OUTPut{self.channel_idx}:POLarity?")

    @polarity.setter
    def polarity(self, val: str = "NORMal") -> None:
        """
        Set the output polarity of the AFG.

        Args:
            val (str, optional): The output polarity to set. Defaults to "NORMal".
        """
        self.write(f"OUTPut{self.channel_idx}:POLarity {val}")

    @property
    def trigger_out_mode(self) -> str:
        """
        Get the trigger output mode of the AFG.

        Returns:
            str: The trigger output mode of the AFG.
        """
        return self.ask("OUTPut:TRIGger:MODE?")

    @trigger_out_mode.setter
    def trigger_out_mode(self, val: str = "TRIGger") -> None:
        """
        Set the trigger output mode of the AFG.

        Args:
            val (str, optional): The trigger output mode to set. Defaults to "TRIGger".
        """
        self.write(f"OUTPut:TRIGger:MODE {val}")

    @property
    def ref_oscillator(self) -> str:
        """
        Get the reference oscillator source of the AFG.

        Returns:
            str: The reference oscillator source of the AFG.
        """
        return self.ask("SOURce:ROSCillator:SOURce?")

    @ref_oscillator.setter
    def ref_oscillator(self, val: str = "EXT") -> None:
        """
        Set the reference oscillator source of the AFG.

        Args:
            val (str, optional): The reference oscillator source to set. Defaults to "EXT".
        """
        self.write(f"SOURce:ROSCillator:SOURce {val}")

    @property
    def amplitude_lock(self) -> bool:
        """
        Check if the voltages of both channels are locked to each other.

        Returns:
            bool: True if the voltages of both channels are locked, False otherwise.
        """
        return self.ask(f"SOURCe{self.channel_idx}:VOLTage:CONCurrent:STATe?") == "1"

    @amplitude_lock.setter
    def amplitude_lock(self, val: bool) -> None:
        """
        Lock or unlock the voltages of both channels to each other.

        Args:
            val (bool): True to lock the voltages, False to unlock.
        """
        if val:
            self.write(f"SOURCe{self.channel_idx}:VOLTage:CONCurrent:STATe ON")
        else:
            self.write(f"SOURCe{self.channel_idx}:VOLTage:CONCurrent:STATe OFF")

    @property
    def frequency_lock(self) -> bool:
        """
        Check if the frequencies of both channels are locked to each other.

        Returns:
            bool: True if the frequencies of both channels are locked, False otherwise.
        """
        return self.ask(f"SOURCe{self.channel_idx}:FREQuency:CONCurrent:STATe?") == "1"

    @frequency_lock.setter
    def frequency_lock(self, val) -> None:
        """
        Lock or unlock the frequencies of both channels to each other.

        Args:
            val: True to lock the frequencies, False to unlock.
        """
        if val:
            self.write(f"SOURCe{self.channel_idx}:FREQuency:CONCurrent:STATe ON")
        else:
            self.write(f"SOURCe{self.channel_idx}:FREQuency:CONCurrent:STATe OFF")

    # numerical values
    @property
    def amplitude(self) -> float:
        """
        Get the signal amplitude in Vpp.

        Returns:
            float: The signal amplitude in Vpp.
        """
        return float(
            self.ask(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:AMPLitude?")
        )

    @amplitude.setter
    def amplitude(self, val: float = 0) -> None:
        """
        Set the signal amplitude in Vpp.

        Args:
            val (float, optional): The signal amplitude to set in Vpp. Defaults to 0.
        """
        self.write(
            f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:AMPLitude {val:f}VPP"
        )

    @property
    def frequency(self) -> float:
        """
        Get the frequency of the AFG.

        Returns:
            float: The frequency of the AFG.
        """
        return float(self.ask(f"SOURCe{self.channel_idx}:FREQuency:FIXed?"))

    @frequency.setter
    def frequency(self, val: float = 0) -> None:
        """
        Set the frequency of the AFG.

        Args:
            val (float, optional): The frequency to set. Defaults to 0.
        """
        self.write(f"SOURCe{self.channel_idx}:FREQuency:FIXed {val:f}Hz")

    @property
    def phase(self) -> float:
        """
        Get or set the phase in degrees.

        Args:
            value (float, optional): The phase to set in degrees. Defaults to 0.

        Returns:
            float: The phase in degrees.
        """
        return (
            180.0 / np.pi * float(self.ask(f"SOURce{self.channel_idx}:PHASe:ADJust?"))
        )

    @phase.setter
    def phase(self, value: float = 0) -> None:
        value = value % 360.0
        while value > 180.0:
            value -= 360.0
        self.write(f"SOURce{self.channel_idx}:PHASe:ADJust {value:.2f} DEG")

    @property
    def offset(self) -> float:
        """
        Get or set the offset.

        Args:
            val (float, optional): The offset to set. Defaults to 0.

        Returns:
            float: The offset.
        """
        return float(
            self.ask(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:OFFSet?")
        )

    @offset.setter
    def offset(self, val: float = 0) -> None:
        self.write(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:OFFSet {val:f}V")

    @property
    def high(self) -> float:
        """
        Get or set the high value for voltage.

        Args:
            value (float, optional): The high value for voltage to set. Defaults to 0.

        Returns:
            float: The high value for voltage.
        """
        return float(
            self.ask(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:HIGH?")
        )

    @high.setter
    def high(self, value: float = 0) -> None:
        self.write(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:HIGH {value:f}V")

    @property
    def low(self) -> float:
        """
        Get or set the low value for voltage.

        Args:
            value (float, optional): The low value for voltage to set. Defaults to 0.

        Returns:
            float: The low value for voltage.
        """
        return float(self.ask(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:LOW?"))

    @low.setter
    def low(self, value: float = 0) -> None:
        self.write(f"SOURce{self.channel_idx}:VOLTage:LEVel:IMMediate:LOW {value:f}V")

    @property
    def trigger_source(self) -> str:
        """Get or set the trigger source of the AFG.

        Returns:
            str: The trigger source of the AFG.
        """
        return self.ask("TRIGger:SEQuence:SOURce?")

    @trigger_source.setter
    def trigger_source(self, val: str = "TIM") -> None:
        self.write(f"TRIGger:SEQuence:SOURce {val}")

    @property
    def trigger_slope(self) -> str:
        """Get or set the trigger slope of the AFG.

        Args:
            val (str, optional): The trigger slope to set. Defaults to "POS".

        Returns:
            str: The trigger slope of the AFG.
        """
        return self.ask("TRIGger:SEQuence:SLOPe?")

    @trigger_slope.setter
    def trigger_slope(self, val: str = "POS") -> None:
        self.write(f"TRIGger:SEQuence:SLOPe {val}")

    @property
    def trigger_timer(self) -> float:
        """Get or set the trigger timer of the AFG.

        Args:
            value (float, optional): The trigger timer to set. Defaults to 1.
        Returns:
            float: The trigger timer of the AFG.
        """
        return float(self.ask("TRIGger:SEQuence:TIMer?"))

    @trigger_timer.setter
    def trigger_timer(self, value: float = 1) -> None:
        self.write(f"TRIGger:SEQuence:TIMer {value}s")

    def trigger(self) -> None:
        """Trigger the measurement."""
        self.write("TRIGger:SEQuence:IMMediate")

    @property
    def burst_enabled(self) -> bool:
        """Get or set the burst mode state of the AFG.


        Returns:
            bool: If burst mode is enabled.
        """
        return self.ask(f"SOURce{self.channel_idx}:BURst:STATe?") == "1"

    @burst_enabled.setter
    def burst_enabled(self, value: ONOFF_TYPE) -> None:
        if self._value_to_bool(value):
            self.write(f"SOURce{self.channel_idx}:BURst:STATe ON")
        else:
            self.write(f"SOURce{self.channel_idx}:BURst:STATe OFF")

    @property
    def burst_cycles(self) -> int:
        """Get or set the number of burst cycles of the AFG."""
        return int(self.ask(f"SOURce{self.channel_idx}:BURst:NCYCles?"))

    @burst_cycles.setter
    def burst_cycles(self, value: int = 1) -> None:
        self.write(f"SOURce{self.channel_idx}:BURst:NCYCles {int(value)}")

    @property
    def burst_delay(self) -> float:
        """Get or set the burst delay of the AFG."""
        return float(self.ask(f"SOURce{self.channel_idx}:BURst:TDelay?"))

    @burst_delay.setter
    def burst_delay(self, value: float = 0.0) -> None:
        self.write(f"SOURce{self.channel_idx}:BURst:TDelay {value:f}s")

    @property
    def burst_mode(self) -> str:
        """Get or set the burst mode of the AFG."""
        return self.ask(f"SOURce{self.channel_idx}:BURst:MODE?")

    @burst_mode.setter
    def burst_mode(self, value: str = "TRIG") -> None:
        self.write(f"SOURce{self.channel_idx}:BURst:MODE {value}")

    def sweep(self, start_freq: float, stop_freq: float, sweep_time: float) -> None:
        """Perform a frequency sweep on the AFG.

        Args:
            start_freq (float): The starting frequency of the sweep.
            stop_freq (float): The stopping frequency of the sweep.
            sweep_time (float): The duration of the sweep in seconds.
        """

        self.write(f"SOURce{self.channel_idx}:FREQuency:STARt {start_freq:f}Hz")
        self.write(f"SOURce{self.channel_idx}:FREQuency:STOP {stop_freq:f}Hz")
        self.write(f"SOURce{self.channel_idx}:SWEep:TIME {sweep_time:f}s")
        self.write(f"SOURce{self.channel_idx}:SWEep:MODE AUTO")
        self.write(f"SOURce{self.channel_idx}:SWEep:STATe ON")
