
import pwmio
import TerrainTronics.D1MiniBoardBase
from LumensalisCP.Main.Expressions import NamedOutputTarget, EvaluationContext
from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
import digitalio, analogio
import adafruit_74hc595
from adafruit_bus_device import spi_device
import busio, math, digitalio
from LumensalisCP.Triggers.Timer import PeriodicTimer

class HarlechLED(NamedOutputTarget):

    def __init__(self, name, index, board=None ):
        NamedOutputTarget.__init__(self, name=name)
        print(f'HarlechLED {name} [{index}]')
        self.__board:"HarlechCastle" = board
        self.__index = index
        self.__value = 0
        
    def set(self, level:float, context:EvaluationContext = None):
        if type(level) is not float:
            if level is True: level = 1.0
            elif level is False:  level = 0.0
            else: level = float(level)
            
        self.__value = level
        self.__board._values[self.__index] = level

        
    @property
    def value(self): return self.__value
    
    def __repr__(self):
        return f"HarlechLED( {self.name}, {self.__index}, v={self.__value} )"

class KeepAlive(Debuggable):
    def __init__(self, castle:"HarlechCastle", 
                keepAlivePin=None,
                keepAliveCycle:TimeInSeconds = 8.0,
                keepAlivePulse:TimeInSeconds = 1.0,
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
     
    def _timerHit(self,when:float=None, **kwds):
        
        if self.__nextPulse <= when:
            self.dbgOut( "start pulse" )
            #print( "start pulse" )
            self._setKeepAlive( True )
            self.__nextPulse = when + self.__keepAliveCycle
            self.__nextPulseEnd = when + self.__keepAlivePulse
        else:
            if self.__state:
                self.dbgOut( "end pulse" )
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

class HarlechCastle(TerrainTronics.D1MiniBoardBase.D1MiniBoardBase):
    OE_DUTY_CYCLE = 65535
    OE_PWM_FREQUENCY = 500
        
    def __init__(self, *args,
                name=None, 
                version:str=None,
                oePin:str=None,
                brightness = 1.0,
                ledRefreshRate:float = 50.0,
                refreshRate=0.001,
                addKeepAlive = True,
                keepAlivePin=None,
                keepAliveCycle:float=None,
                keepAlivePulse:float=None,
                baudrate=1000000,
                oeBrightness=True, 
                 **kwds ):
        
        
        
        name = name or "Harlech"
        super().__init__( *args, name=name, refreshRate=refreshRate, **kwds )
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
        
        self.__leds:List[HarlechLED] = [None,None,None,None,None,None,None,None]
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



