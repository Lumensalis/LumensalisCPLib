
# based on https://github.com/eosti/micropython-aw210xx/blob/main/src/aw210xx.py
#from machine import I2C

TYPE_CHECKING = False
if TYPE_CHECKING:
    from enum import IntEnum
    from typing import Optional
else:
    IntEnum = object
    Optional = object

from LumensalisCP.common import *

__version__ = "1.0.0"

from adafruit_bus_device import i2c_device

class AW210xxRegisters(IntEnum):
    """
    Enum for all registers on a AW210xx. Any _BASE registers represent the
    0th register with that name, the number of additional registers
    is dependent on model
    """

    GCR = 0x00
    BR_BASE = 0x01
    UPDATE = 0x49
    COL_BASE = 0x4A
    GCCR = 0x6E
    PHCR = 0x70
    OSDCR = 0x71
    OSST_BASE = 0x72
    OTCR = 0x77
    SSCR = 0x78
    UVCR = 0x79
    GCR2 = 0x7A
    GCR4 = 0x7C
    VER = 0x7E
    RESET = 0x7F
    WBR = 0x90
    WBG = 0x91
    WBB = 0x92
    PATCFG = 0xA0
    PATGO = 0xA1
    PATT0 = 0xA2
    PATT1 = 0xA3
    PATT2 = 0xA4
    PATT3 = 0xA5
    FADEH = 0xA6
    FADEL = 0xA7
    GCOLR = 0xA8
    GCALG = 0xA9
    GCOLB = 0xAA
    GCFG0 = 0xAB
    GCFG1 = 0xAC


class AW210xxPWMFrequency(IntEnum):
    """
    Enum for PWM frequency selection
    The PWM values are a function of the OSC frequency selection,
        which is actually being changed with these
    """

    FREQ_62K = 0b000
    FREQ_32K = 0x001
    FREQ_4K = 0b010
    FREQ_2K = 0b011
    FREQ_1K = 0b100
    FREQ_500 = 0b101
    FREQ_244 = 0b110
    FREQ_122 = 0b111


class AW210xxOpenShortDetect(IntEnum):
    """Enum for open/short detection mode selection"""

    DISABLE = 0b00
    SHORT_ENABLE = 0b10
    OPEN_ENABLE = 0b11


class AW210xxOpenThreshold(IntEnum):
    """Enum for open-circuit threshold, relative to above GND"""

    VOLTAGE_100MV = 0
    VOLTAGE_200MV = 1


class AW210xxShortThreshold(IntEnum):
    """Enum for short-circuit threshold, relative to below VDD"""

    VOLTAGE_1V = 0
    VOLTAGE_500MV = 1


class AW210xxRisingSlewRate(IntEnum):
    """Enum for the rising time of the LED"""

    RATE_1NS = 0
    RATE_6NS = 1


class AW210xxFallingSlewRate(IntEnum):
    """Enum for the falling time of the LED"""

    RATE_1NS = 0b00
    RATE_3NS = 0b01
    RATE_6NS = 0b10
    RATE_10NS = 0b11


class AW210xxThermalThreshold(IntEnum):
    """Enum for the thermal roll-off threshold"""

    TEMP_140C = 0b00
    TEMP_120C = 0b01
    TEMP_100C = 0b10
    TEMP_90C = 0b11


class AW210xxThermalRollOffPercentage(IntEnum):
    """Enum for the IOUT roll-off thermal protection"""

    PERCENT_100 = 0b00
    PERCENT_75 = 0b01
    PERCENT_55 = 0b10
    PERCENT_30 = 0b11


class AW210xxSpreadSpectrumRange(IntEnum):
    """Enum for the percent frequency deviation during spread spectrum"""

    PERCENT_05 = 0b00
    PERCENT_15 = 0b01
    PERCENT_25 = 0b10
    PERCENT_35 = 0b11


class AW210xxSpreadSpectrumTime(IntEnum):
    """Enum for the cycle time of spread spectrum"""

    TIME_1980US = 0b00
    TIME_1200US = 0b01
    TIME_820US = 0b10
    TIME_660US = 0b11


class AW210xxREXTStatus(IntEnum):
    """Enum for the status of R_ext"""

    NORMAL = 0b00
    OPEN = 0b01
    SHORT_OCP = 0b10
    UNDEFINED = 0b11


class AW210xxOCPThreshold(IntEnum):
    """Enum for the OCP threshold"""

    OCP_85MA = 0
    OCP_55MA = 1


class AW210xxBase(Debuggable):
    """Base class for AW210xx with init and R/W functions"""

    def __init__(
        self, i2c, #: I2C
         address: int = 0x30, model: str = "AW21024", r_ext: float = 4000
    ):
        super().__init__()
        self.i2c = i2c_device.I2CDevice(i2c, address)
        self.addr = address
        self.r_ext = 4000
        self.model = model
        self._buffer = bytearray(2)

        if model == "AW21009":
            self.NUM_CHANNELS = 9
        elif model == "AW21012":
            self.NUM_CHANNELS = 12
        elif model == "AW21018":
            self.NUM_CHANNELS = 18
        elif model == "AW21024":
            self.NUM_CHANNELS = 24
        elif model == "AW21036":
            self.NUM_CHANNELS = 36
        else:
            raise ValueError("Unknown AW210xx model")

    def _read_register(self, register: int, lock:bool = True) -> int:
        
        if lock:
            with self.i2c:
                self.i2c.write_then_readinto(bytes([register]), self._buffer, in_end=1)
        else:
            self.i2c.write_then_readinto(bytes([register]), self._buffer, in_end=1)
        rv = int( self._buffer[0])
        self.dbgOut( "_read_register(%.X)=%X", register, rv )
        return rv
        # return int(self.i2c.readfrom_mem(self.addr, register, 1)[0])

    def _write_register(self, register: int, val: int) -> None:
        self.dbgOut( "_write_register(%.X)=%X", register, val )
        with self.i2c:
            self.i2c.write(bytes([register, val]))

    def _read_bits(self, register: int, pos: int, numbits: int) -> int:
        """Read from certain bits in a register"""
        if pos + numbits > 8:
            raise ValueError("Cannot read more than 8 bits from a byte")
        mask = (2**numbits) - 1 << pos
        
        reg = self._read_register( register )
        return (reg & mask) >> pos

    def _write_bits(self, register: int, pos: int, numbits: int, state: int) -> None:
        """Write to certain bits in a register"""
        if pos + numbits > 8:
            raise ValueError("Cannot write more than 8 bits to a byte")
        mask = (2**numbits) - 1 << pos
        
        with self.i2c:
            #reg = int(self.i2c.readfrom_mem(self.addr, register, 1)[0])
            reg = self._read_register( register, lock=False )
            retval = (reg & ~mask) | ((state << pos) & mask)
            self.i2c.write( bytes([register, retval]))
            # self.i2c.write(self.addr, register, bytearray([retval]))
            #self.i2c.writeto_mem(self.addr, register, bytearray([retval]))


class AW210xxBasic(AW210xxBase):
    """Collection of basic functions of the chip"""

    def get_version(self) -> int:
        """Get the chip version"""
        return self._read_register(AW210xxRegisters.VER)

    def get_id(self) -> int:
        """Get the chip ID = 0x18"""
        return self._read_register(AW210xxRegisters.RESET)

    def reset(self) -> None:
        """Reset registers to default state"""
        self._write_register(AW210xxRegisters.RESET, 0x00)

    def chip_enabled(self, enabled: Optional[bool] = None) -> bool:
        """Set or get chip enable state"""
        if enabled is None:
            return bool(self._read_bits(AW210xxRegisters.GCR, 0, 1))
        self._write_bits(AW210xxRegisters.GCR, 0, 1, enabled)
        return enabled


class AW210xxLED(AW210xxBase):
    """Collection of functions changing the control of LEDs"""

    def rgb_mode(self, state: Optional[bool] = None) -> bool:
        """
        Set or get the state of RGB mode
        (every 3 channels share common brightness)
        """
        if state is None:
            return bool(self._read_bits(AW210xxRegisters.GCR2, 0, 1))
        self._write_bits(AW210xxRegisters.GCR2, 0, 1, state)
        return state

    def white_scaling(self, wb: Optional[tuple] = None) -> tuple:
        """Set or get the output white balance as a tuple (R, G, B)"""
        if wb is None:
            r_wb = self._read_register(AW210xxRegisters.WBR)
            g_wb = self._read_register(AW210xxRegisters.WBG)
            b_wb = self._read_register(AW210xxRegisters.WBB)
            return (r_wb, g_wb, b_wb)

        self._write_register(AW210xxRegisters.WBR, wb[0])
        self._write_register(AW210xxRegisters.WBG, wb[1])
        self._write_register(AW210xxRegisters.WBB, wb[2])
        return wb

    def rise_slewrate(
        self, rate: Optional[AW210xxRisingSlewRate] = None
    ) -> AW210xxRisingSlewRate:
        """Set or get the LED rising edge slew rate"""
        if rate is None:
            return AW210xxRisingSlewRate(self._read_bits(AW210xxRegisters.GCR4, 2, 1))
        self._write_bits(AW210xxRegisters.GCR4, 2, 1, rate)
        return rate

    def fall_slewrate(
        self, rate: Optional[AW210xxFallingSlewRate] = None
    ) -> AW210xxFallingSlewRate:
        """Set or get the LED falling edge slew rate"""
        if rate is None:
            return AW210xxFallingSlewRate(self._read_bits(AW210xxRegisters.GCR4, 0, 2))
        self._write_bits(AW210xxRegisters.GCR4, 0, 2, rate)
        return rate

    def br(self, channel: int, val: Optional[int] = None) -> int:
        """Set or get the PWM brightness for a certain channel"""
        if channel < 0 or channel > self.NUM_CHANNELS - 1:
            raise ValueError(f"Channel number must be between 0 and {self.NUM_CHANNELS - 1}")

        if val is None:
            return self._read_register(AW210xxRegisters.BR_BASE + channel)

        if val < 0 or val > 255:
            raise ValueError(
                "Channel brightness scalar must be between 0 and 255 inclusive"
            )

        self._write_register(AW210xxRegisters.BR_BASE + channel, val)
        return val

    def update(self):
        """Update output to match current state of BR registers"""
        self._write_register(AW210xxRegisters.UPDATE, 0x00)


class AW210xxOpenShortChecking(AW210xxBase):
    """Collection of functions related to the open/short circuit detection"""

    def open_threshold(
        self, thresh: Optional[AW210xxOpenThreshold] = None
    ) -> AW210xxOpenThreshold:
        """Set or get the open circuit threshold"""
        if thresh is None:
            return AW210xxOpenThreshold(self._read_bits(AW210xxRegisters.OSDCR, 3, 1))
        self._write_bits(AW210xxRegisters.OSDCR, 3, 1, thresh)
        return thresh

    def short_threshold(
        self, thresh: Optional[AW210xxShortThreshold] = None
    ) -> AW210xxShortThreshold:
        """Set or get the short circuit threshold"""
        if thresh is None:
            return AW210xxShortThreshold(self._read_bits(AW210xxRegisters.OSDCR, 2, 1))
        self._write_bits(AW210xxRegisters.OSDCR, 2, 1, thresh)
        return thresh

    def open_short_detect(
        self, thresh: Optional[AW210xxOpenShortDetect] = None
    ) -> AW210xxOpenShortDetect:
        """Set or get the short/open detect state"""
        if thresh is None:
            return AW210xxOpenShortDetect(self._read_bits(AW210xxRegisters.OSDCR, 0, 2))
        self._write_bits(AW210xxRegisters.OSDCR, 0, 2, thresh)
        return thresh

    def get_open_short_status(self) -> int:
        """Reads open/short status register and returns concatenated bitfield"""
        state = 0
        for i in range(5):
            state = state | self._read_register(AW210xxRegisters.OSST_BASE + i) << (
                8 * i
            )
        return state


class AW210xxPWM(AW210xxBase):
    """Collection of functions relating to PWM configuration"""

    def pwm_sel(
        self, freq: Optional[AW210xxPWMFrequency] = None
    ) -> AW210xxPWMFrequency:
        """Set or get output PWM frequency"""
        if freq is None:
            return AW210xxPWMFrequency(self._read_bits(AW210xxRegisters.GCR, 4, 3))
        self._write_bits(AW210xxRegisters.GCR, 4, 3, freq)
        return freq

    def pwm_phase_delay(self, state: Optional[bool] = None) -> bool:
        """Sets or gets the PWM phase delay state"""
        if state is None:
            return bool(self._read_bits(AW210xxRegisters.PHCR, 7, 1))
        self._write_bits(AW210xxRegisters.PHCR, 7, 1, state)
        return state

    def set_pwm_phase_invert(self, state: bool) -> None:
        """
        Sets the PWM phase inversion state. I'm lazy so this will
        toggle all inversions at once, i.e. all even channels will become inverted.
        """
        if state is True:
            state_val = 0b11111111
        else:
            state_val = 0
        # TODO: is writing to all the fields ok on smaller chips?
        self._write_bits(AW210xxRegisters.PHCR, 1, 6, state_val)

    def spread_spectrum_enabled(self, enabled: Optional[bool] = None) -> bool:
        """Sets or gets if spread spectrum is enabled"""
        if enabled is None:
            return bool(self._read_bits(AW210xxRegisters.SSCR, 4, 1))
        self._write_bits(AW210xxRegisters.SSCR, 4, 1, enabled)
        return enabled

    def spread_spectrum_range(
        self, state: Optional[AW210xxSpreadSpectrumRange] = None
    ) -> AW210xxSpreadSpectrumRange:
        """Sets or gets the frequency range that the frequency will spread across"""
        if state is None:
            return AW210xxSpreadSpectrumRange(
                self._read_bits(AW210xxRegisters.SSCR, 2, 2)
            )
        self._write_bits(AW210xxRegisters.SSCR, 2, 2, state)
        return state

    def spread_spectrum_cycletime(
        self, state: Optional[AW210xxSpreadSpectrumTime] = None
    ) -> AW210xxSpreadSpectrumTime:
        """Sets or gets the cycle time of spread spectrum"""
        if state is None:
            return AW210xxSpreadSpectrumTime(
                self._read_bits(AW210xxRegisters.SSCR, 0, 2)
            )
        self._write_bits(AW210xxRegisters.SSCR, 0, 2, state)
        return state

    def fixed_on(self, state: bool) -> None:
        """Sets all LEDs to max BRightness"""
        if state:
            write_var = 0b111
        else:
            write_var = 0b000
        self._write_bits(AW210xxRegisters.SSCR, 5, 3, write_var)


class AW210xxPower(AW210xxBase):
    """Collection of functions related to power and power protection"""

    def power_saving(self, state: Optional[bool] = None) -> bool:
        """Set or get power saving state"""
        if state is None:
            return bool(self._read_bits(AW210xxRegisters.GCR, 7, 1))
        self._write_bits(AW210xxRegisters.GCR, 7, 1, state)
        return state

    def global_current(self, val: Optional[int] = None) -> int:
        """Set or get the global current scalar (0-255)"""
        if val is None:
            return self._read_register(AW210xxRegisters.GCCR)

        if val < 0 or val > 255:
            raise ValueError(
                "Global current scalar must be between 0 and 255 inclusive"
            )

        self._write_register(AW210xxRegisters.GCCR, val)
        return val

    def col(self, channel: int, val: Optional[int] = None) -> int:
        """Set or get the constant current parameter for a certain channel"""
        if channel < 0 or channel > self.NUM_CHANNELS - 1:
            raise ValueError(f"Channel number must be between 0 and {self.NUM_CHANNELS - 1}")

        if val is None:
            return self._read_register(AW210xxRegisters.COL_BASE + channel)

        if val < 0 or val > 255:
            raise ValueError(
                "Channel current scalar must be between 0 and 255 inclusive"
            )

        self._write_register(AW210xxRegisters.COL_BASE + channel, val)
        return val

    def uvlo_detected(self) -> bool:
        """Reads if an UVLO has been detected"""
        return bool(self._read_bits(AW210xxRegisters.UVCR, 5, 1))

    def por_status(self) -> bool:
        """Reads power on reset state. Note: cleared on read"""
        return bool(self._read_bits(AW210xxRegisters.UVCR, 4, 1))

    def rext_status(self) -> AW210xxREXTStatus:
        """Reads state of R_ext"""
        return AW210xxREXTStatus(self._read_bits(AW210xxRegisters.UVCR, 7, 2))

    def ocp_threshold(
        self, state: Optional[AW210xxOCPThreshold] = None
    ) -> AW210xxOCPThreshold:
        """Set or get the overcurrent protection threshold"""
        if state is None:
            return AW210xxOCPThreshold(self._read_bits(AW210xxRegisters.UVCR, 3, 1))
        self._write_bits(AW210xxRegisters.UVCR, 3, 1, state)
        return state

    def ocp_enabled(self, enabled: Optional[bool] = None) -> bool:
        """Set or get the overcurrent protection state"""
        if enabled is None:
            return bool(self._read_bits(AW210xxRegisters.UVCR, 2, 1))
        self._write_bits(AW210xxRegisters.UVCR, 2, 1, enabled)
        return enabled

    def uvlo_protection_disabled(self, disabled: Optional[bool] = None) -> bool:
        """
        Set or get if the UVLO protection (i.e. action) is disabled
        When tripped, the UVLO protection disables the chip.
        To function, the UVLO detection must also be enabled.
        """
        if disabled is None:
            return bool(self._read_bits(AW210xxRegisters.UVCR, 1, 1))
        self._write_bits(AW210xxRegisters.UVCR, 1, 1, disabled)
        return disabled

    def uvlo_detection_disabled(self, disabled: Optional[bool] = None) -> bool:
        """
        Set or get if the UVLO detection is disabled
        When tripped, the UVLO detection will set undervoltage bit, see `uvlo_detected()`
        """
        if disabled is None:
            return bool(self._read_bits(AW210xxRegisters.UVCR, 0, 1))
        self._write_bits(AW210xxRegisters.UVCR, 0, 1, disabled)
        return disabled

    def max_current(self) -> float:
        """
        Returns max possible current per channel.
        Assumes that white correction is at max, global current control is at max,
        and BR and COL for the channel is at max.
        """
        return 200 * 0.4 / self.r_ext

    def max_global_current(self) -> float:
        """
        Taking into account the global current control,
        returns max current per channel.
        """
        return self.max_current() * self.global_current() / 255


class AW210xxThermalProtection(AW210xxBase):
    """Collection of functions for configuring overtemperature protection"""

    def ot_detected(self) -> bool:
        """Reads if there is an overtemperature event"""
        return bool(self._read_bits(AW210xxRegisters.OTCR, 4, 1))

    def ot_protection_disabled(self, disabled: Optional[bool] = None) -> bool:
        """
        Set or get if the overtemperature protection (i.e. action) is disabled
        When tripped, the OT protection disables the chip.
        The setpoint of overtemperature is 150C.
        To function, the OT detection must also be enabled.
        """
        if disabled is None:
            return bool(self._read_bits(AW210xxRegisters.OTCR, 3, 1))
        self._write_bits(AW210xxRegisters.OTCR, 3, 1, disabled)
        return disabled

    def ot_detection_disabled(self, disabled: Optional[bool] = None) -> bool:
        """
        Set or get if the overtemperature protection (i.e. action) is disabled
        When tripped, the OT detection will set OT bit, see `ot_detected()`
        The setpoint of overtemperature is 150C.
        """
        if disabled is None:
            return bool(self._read_bits(AW210xxRegisters.OTCR, 2, 1))
        self._write_bits(AW210xxRegisters.OTCR, 2, 1, disabled)
        return disabled

    def thermal_rolloff(self) -> bool:
        """Reads if there is thermal roll-off occurring"""
        return bool(self._read_bits(AW210xxRegisters.OTCR, 5, 1))

    def thermal_rolloff_threshold(
        self, temp: Optional[AW210xxThermalThreshold] = None
    ) -> AW210xxThermalThreshold:
        """Set or get the thermal threshold for current rolloff"""
        if temp is None:
            return AW210xxThermalThreshold(self._read_bits(AW210xxRegisters.OTCR, 0, 2))
        self._write_bits(AW210xxRegisters.OTCR, 0, 2, temp)
        return temp

    def thermal_rolloff_percent(
        self, temp: Optional[AW210xxThermalRollOffPercentage] = None
    ) -> AW210xxThermalRollOffPercentage:
        """Set or get the percentage of Iout to roll-off once the threshold is exceeded"""
        if temp is None:
            return AW210xxThermalRollOffPercentage(
                self._read_bits(AW210xxRegisters.OTCR, 6, 2)
            )
        self._write_bits(AW210xxRegisters.OTCR, 6, 2, temp)
        return temp


class AW210xxPattern(AW210xxBase):
    """Collection of functions related to the built-in effects engine"""

    pass


class AW210xxGroups(AW210xxBase):
    """Collection of functions related to grouping channels"""

    pass


# This is called a mixin, by the way
class AW210xx(
    AW210xxBasic,
    AW210xxLED,
    AW210xxOpenShortChecking,
    AW210xxPWM,
    AW210xxPower,
    AW210xxThermalProtection,
    AW210xxPattern,
    AW210xxGroups,
):
    """Top-level class of AW210xx with all functionality"""

    def max_channel_current(self, channel: int) -> float:
        """
        Taking into account all factors, returns average output current that
        a given channel can pull right now
        """
        wb = self.white_scaling()
        if channel % 3 == 0:
            white_scalar = wb[0]
        elif channel % 3 == 1:
            white_scalar = wb[1]
        else:
            white_scalar = wb[2]

        return (
            self.max_global_current()
            * white_scalar
            / 255
            * self.col(channel)
            / 255
            * self.br(channel)
            / 255
        )