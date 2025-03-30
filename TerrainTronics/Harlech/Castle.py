
import pwmio
import TerrainTronics.D1MiniBoardBase
from LumensalisCP.Main.Expressions import OutputTarget, EvaluationContext
from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
import digitalio, analogio
import adafruit_74hc595
from adafruit_bus_device import spi_device
import busio

class HarlechLED(OutputTarget):
    def __init__(self, name, index, board=None ):
        OutputTarget.__init__(self, name=name)
        print(f'HarlechLED {name} [{index}]')
        self.__board:"HarlechCastle" = board
        self.__index = index
        self.__value = 0
        #self.pwm = pwmio.PWMOut( pin, frequency=50, duty_cycle=0 )
        #self.dac = analogio.AnalogOut(pin)
        
    def set(self, level:float, context:EvaluationContext = None):
        level = float(level)
        self.__value = level
        #self.__dc =  int( max(0.0, min(level,1.0)) * 65535.0 )
        self.__board._values[self.__index] = level
        #dc = int( max(0.0, min(level,1.0)) * 65535.0 )
        #print(f'set HarlechLED {self.name} to {level} = {dc}')
        #self.pwm.duty_cycle = dc
        #self.dac.value = dc 
        
    @property
    def value(self): return self.__value
    
    def __repr__(self):
        return f"HarlechLED( {self.name}, {self.__index}, v={self.__value} )"
        
        
class HarlechCastle(TerrainTronics.D1MiniBoardBase.D1MiniBoardBase):
    def __init__(self, *args, name=None, refreshRate:float = 50.0, **kwds ):
        name = name or "Harlech"
        super().__init__( *args, name=name, **kwds )
        c = self.config
        c.updateDefaultOptions( )
        
        self.__leds:List[HarlechLED] = [None,None,None,None,None,None,None,None]
        self._values:List[float] = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        
        KEEP_ALIVE = self.D0
        HPC_LATCH = self.D8
        HPC_CLOCK = self.D5
        HPC_DATA = self.D6
        
        self.__latch_pin = digitalio.DigitalInOut(HPC_LATCH.actualPin)
        
        self.__spi = busio.SPI(clock=HPC_CLOCK.actualPin, MOSI=HPC_DATA.actualPin )
        
        self._device = spi_device.SPIDevice(self.__spi, self.__latch_pin ,
                                            baudrate=1000000
                                            #baudrate=10000
                                            )
        #self._number_of_shift_registers = number_of_shift_registers
        self._gpio = bytearray(1)
        
        #self.__shift_register = adafruit_74hc595.ShiftRegister74HC595(self.__spi, self.__latch_pin)
        #self.__lastUpdate = self.main.when
        self.__refreshRate = float(refreshRate)
        
        
        def setOutput( pinProxy, value ):
            output =  digitalio.DigitalInOut(pinProxy.actualPin)
            output.switch_to_output(value=value)
            output.value = value
    
    
        self._oe =  setOutput( self.D3, True )#pwmio.PWMOut(self.D3.actualPin,frequency=5000,duty_cycle=65535)
        self._oe2 = setOutput( self.D7, True ) # pwmio.PWMOut(self.D7.actualPin,frequency=5000,duty_cycle=65535)
      
        self._keepAlive = setOutput( KEEP_ALIVE, False )

        
    @property
    def values(self): return self._values
    
    def _update(self):
        #lc = self.__lastUpdate
        pwm_position = divmod(self.main.when, 1/self.__refreshRate)[1]*self.__refreshRate
        
        shift_v = 0
        for i in range(8):
            if self._values[i] > pwm_position:
                shift_v += 2 ** i

        try:

            #b = bytearray(1)
            self._gpio[0] = shift_v
            #print(f'SV {shift_v:2.2X} at {pwm_position:.3f} for {self._values}' )
            with self._device as spi:
                # pylint: disable=no-member
                spi.write(self._gpio)
        except Exception as inst:
            print( f"harlech update exception {inst}, shift_v={shift_v} pwm_position={pwm_position}")
            
    def led(self,ledx:int, name:str = None ) -> HarlechLED:
        rv = self.__leds[ledx]
        if rv is None:
            assert name is not None
            rv = HarlechLED( name=name, index = ledx, board = self)
            self.__leds[ledx] = rv
        else:
            assert name is None or name == rv.name
        return rv



