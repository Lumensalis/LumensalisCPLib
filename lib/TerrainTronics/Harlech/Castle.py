
from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler
__profileImport = getImportProfiler(__name__, globals())

#############################################################################
import pwmio
import digitalio
from adafruit_bus_device import spi_device
import busio, math, microcontroller

from TerrainTronics.D1MiniBoardBase import D1MiniBoardBase, D1MiniPinProxy
from LumensalisCP.IOContext import *
from LumensalisCP.Triggers.Timer import PeriodicTimer

__profileImport.parsing()

#pyright: reportPrivateUsage=false

HarlechPinArg:TypeAlias = Union[ str, microcontroller.Pin, D1MiniPinProxy ]
class HarlechLED(NamedOutputTarget):

    def __init__(self, name:str, index:int, board:HarlechCastle ):
        NamedOutputTarget.__init__(self, name=name)
        print(f'HarlechLED {name} [{index}]')
        self.__board:"HarlechCastle" = board
        self.__index = index
        self.__value = 0
        
    def set(self, value:float, context:Optional[EvaluationContext] = None):
        if type(value) is not float:
            if value is True: value = 1.0
            elif value is False:  value = 0.0
            else: value = float(value)
            
        self.__value = value
        self.__board._values[self.__index] = value

        
    @property
    def value(self): return self.__value
    
    def __repr__(self):
        return f"HarlechLED( {self.name}, {self.__index}, v={self.__value} )"

class KeepAlive(Debuggable):
    def __init__(self, castle:"HarlechCastle", 
                keepAlivePin:Optional[int]=None,
                keepAliveCycle:TimeSpanInSeconds = 8.0,
                keepAlivePulse:TimeSpanInSeconds = 1.0,
            ):
        Debuggable.__init__(self)
        self.castle = castle
        self.enableDbgOut = True
        self.__pin = keepAlivePin
        self.__output = digitalio.DigitalInOut( self.__pin )
        self.__output.direction = digitalio.Direction.OUTPUT
        self.__output.value = False
        
        self.__state = False
        self.__keepAliveCycle = keepAliveCycle or 8.0
        self.__keepAlivePulse = keepAlivePulse or 1.0
        self.__nextPulse:TimeInSeconds = 0
        self.__nextPulseEnd:TimeInSeconds = 0
           
        self._keepAliveTimer = PeriodicTimer( self.__keepAlivePulse , manager=castle.main.timers, name=f"{castle.name}KeepAlive" )
        
        def checkPulse(**kwds):
            # print( "HKA check pulse...")
            self._timerHit(**kwds)
            
        self._keepAliveTimer.addAction( checkPulse )
        
        castle.main.addExitTask( self._keepAliveShutdown )
        
        def startKeepAliveTimer():
            print( f"starting keep alive timer with {self.__keepAlivePulse}")
            self._keepAliveTimer.start(self.__keepAlivePulse)
            
        castle.main.callLater( startKeepAliveTimer )

    def _setKeepAlive(self,state:bool):
        self.__output.value = state
        self.__state = state
     
    def _timerHit(self,
                  context:EvaluationContext,
                  #when:Optional[float]=None, **kwds
            ) -> None:
        when = context.when
        
        if self.__nextPulse <= when:
            if self.enableDbgOut: self.dbgOut( "start pulse" )
            #print( "start pulse" )
            self._setKeepAlive( True )
            self.__nextPulse = when + self.__keepAliveCycle
            self.__nextPulseEnd = when + self.__keepAlivePulse
        else:
            if self.__state:
                if self.enableDbgOut: self.dbgOut( "end pulse" )
                #print( "end pulse" )
                if self.__nextPulseEnd <= when:
                    self._setKeepAlive( False )
            else:
                #self.dbgOut( f"waiting for next pulse at {self.__nextPulse}" )
                pass
 
    def _keepAliveShutdown(self):
        self.infoOut( "shutting down keepAlive" )
        self._setKeepAlive(False)
        self._keepAliveTimer.stop()
        
    @property
    def lastPulse(self): return self.__lastPulse

class HarlechCastle(D1MiniBoardBase):
    OE_DUTY_CYCLE = 65535
    OE_PWM_FREQUENCY = 500
        
    class KWDS(D1MiniBoardBase.KWDS):
        version: NotRequired[str]
        brightness: NotRequired[ZeroToOne]
        ledRefreshRate: NotRequired[float]
        oePin: NotRequired[str|microcontroller.Pin|D1MiniPinProxy]
        addKeepAlive: NotRequired[bool]
        keepAlivePin: NotRequired[str|microcontroller.Pin]
        keepAliveCycle: NotRequired[TimeInSeconds]
        keepAlivePulse: NotRequired[TimeInSeconds]
        oeBrightness: NotRequired[bool]        

    def __init__(self,#*args,
                #name=None, 
                version:Optional[str]=None,
                oePin:Optional[str]=None,
                brightness:ZeroToOne = 1.0,
                ledRefreshRate:float = 50.0,
                #refreshRate=0.05,
                addKeepAlive:bool = True,
                keepAlivePin:Optional[str|microcontroller.Pin]=None,
                keepAliveCycle:Optional[float]=None,
                keepAlivePulse:Optional[float]=None,
                #baudrate=1000000,
                oeBrightness:bool=True, 
                 **kwds:Unpack[D1MiniBoardBase.KWDS] ):
        
        super().__init__( **kwds )  #@*args, name=name, refreshRate=refreshRate,  **kwds )
                         
        c = self.config
        c.updateDefaultOptions( )
        
        KEEP_ALIVE = self.D0
        HPC_LATCH = self.D8
        HPC_CLOCK = self.D5
        HPC_DATA = self.D6
        
        if addKeepAlive:
            self.keepAlive = KeepAlive(
                self, keepAlivePin=self.asPin(keepAlivePin or KEEP_ALIVE), keepAliveCycle=keepAliveCycle, keepAlivePulse=keepAlivePulse
            )
        
        self.__leds:List[HarlechLED|None] = [None,None,None,None,None,None,None,None]
        self._values:List[float] = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        
        self.__version = version
        if oePin is None:
            if self.__version in [ "1p1", "1.1", 1.1 ]:
                oePin = self.D7
            if self.__version in [ "1p0", "1.0", 1.0 ]:
                oePin = self.D4
        elif type(oePin) is str:
            oePin = getattr(self,oePin)


        self.__latch_pin = digitalio.DigitalInOut(HPC_LATCH.actualPin)
        
        self.__spi = busio.SPI(clock=HPC_CLOCK.actualPin, MOSI=HPC_DATA.actualPin )
        
        self._device = spi_device.SPIDevice(self.__spi, self.__latch_pin, baudrate=baudrate )
        
        self._gpio = bytearray(1)
        self._shiftWrites = 0
        
        self.__ledRefreshRate = None if ledRefreshRate is None else float(ledRefreshRate)
        
  
        def setOutput( pinProxy, value ):
            output =  digitalio.DigitalInOut(pinProxy.actualPin)
            output.switch_to_output(value=value)
            output.value = value
        
        self.__oeBrightnessEnabled = oeBrightness

        def addOePWM( pin ):
            pin = getattr( pin, 'actualPin', pin )
            
            if self.__oeBrightnessEnabled:
                #return analogio.AnalogOut(pin)
                return pwmio.PWMOut(pin=pin, frequency= HarlechCastle.OE_PWM_FREQUENCY,duty_cycle=0 ) # HarlechCastle.OE_DUTY_CYCLE)
            output =  digitalio.DigitalInOut(pin)
            output.switch_to_output(value=1)
            output.value = 1
            return output
        
        self.__oePWMS:List[pwmio.PWMOut] = []
        if oePin:
            self.__oePWMS.append( addOePWM( oePin ) )
        else:
            self.__oePWMS.append( addOePWM( self.D3 ) )
            self.__oePWMS.append( addOePWM( self.D4 ) )
            self.__oePWMS.append( addOePWM( self.D7 ) )

        self.__brightness:float = 0.0
        
        #self._keepAlive = setOutput( KEEP_ALIVE, False )

        #self.main.addTask(self._update)
        
        self.brightness = brightness



    @property
    def values(self): return self._values

    @property
    def brightness(self): return self.__brightness

    @brightness.setter
    def brightness(self, level:float):
        self.__brightness = max(0.0, min( 1.0, float(level) ) )
        
        if self.__brightness >= 1.0:
            duty_cycle =  HarlechCastle.OE_DUTY_CYCLE
        else:
            blog = 10.0
            level = math.log( self.__brightness*(blog-1.0)+1.0, blog )
            duty_cycle = max( 0, min( HarlechCastle.OE_DUTY_CYCLE, int( HarlechCastle.OE_DUTY_CYCLE * level)))
        #print( f"brightness = {level}, duty_cycle={duty_cycle} {self.__oePWMS} ")
        
        self._oeDutyCycle = duty_cycle
        
        if self.__oeBrightnessEnabled:
            for oe in self.__oePWMS:
                oe.duty_cycle = duty_cycle
                #oe.value = duty_cycle
        
        
    @property
    def oePWMS(self): return iter( self.__oePWMS )
    
    def doRefresh(self, context):
        #lc = self.__lastUpdate
        if self.__ledRefreshRate is not None:
            pwm_position = divmod(self.main.when, 1/self.__ledRefreshRate)[1]*self.__ledRefreshRate
        else:
            pwm_position = 0.1
                    
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
            self._shiftWrites += 1
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

__profileImport.complete()
