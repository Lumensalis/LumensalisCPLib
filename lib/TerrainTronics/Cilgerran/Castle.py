from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__profileImport = getImportProfiler( __name__, globals()) 

#############################################################################
# pyright: reportPrivateUsage=false, reportMissingImports=false
# pylint: disable=unused-import,import-error,unused-argument
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false
# pyright: reportUnknownVariableType=false

import microcontroller
from TerrainTronics.D1MiniBoardBase import D1MiniBoardBase
from LumensalisCP.IOContext import *
from LumensalisCP.commonCP import *
from LumensalisCP.Lights.Light import *
from LumensalisCP.Lights.Light import LightSource
from LumensalisCP.Behaviors.Rotation import DCMotorSpinner

#############################################################################
if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager

#############################################################################

__profileImport.parsing()

# pyright: reportPrivateUsage=false

class CilgerranLED( DimmableLight ):

    PWM_FREQUENCY:int = 2000
    DUTY_CYCLE_RANGE:int = 65535

    def __init__(self,
                board:CilgerranCastle, 
                pin:microcontroller.Pin,
                **kwargs:Unpack[DimmableLight.KWDS] ) -> None:
        
        source:LightSource = board.ledSource
        kwargs.setdefault( 'source', source )
        super().__init__( **kwargs )
        #print(f'CilgerranLED {name} [{index}]')
        self.__board:CilgerranCastle = board
        self.__pin = pin
        self.__main = board.main
        #self.__index = index
        self.__value:ZeroToOne = 0.0
        self.__output = pwmio.PWMOut(pin=board.asPin(pin), frequency= CilgerranLED.PWM_FREQUENCY,duty_cycle=0 ) 
        self.__dutyCycle = 0

    @property
    def source(self)->CilgerranPixelSource: return self.__source # type: ignore

    @property
    def pin(self) -> microcontroller.Pin: return self.__pin

    @property
    def dutycycle(self) -> int:
        """ the current duty cycle of the LED """
        return self.__output.duty_cycle

    def setValue(self,value:AnyRGBValue, context: Optional[UpdateContext] = None ):
        context = context or self.__main.latestContext
        if not isinstance(value, float):
            if isinstance(value, int) and value >= 0 and value <= 1:
                value = float(value)
            else:
                if isinstance(value, RGB):
                    value = value.brightness
                else:
                    value = RGB.toRGB(value).brightness
                
        if self.__value != value:
            if self.enableDbgOut: self.dbgOut("setValue changing from %s to %s", self.__value, value)
            self.__value = value    
            self._brightnessChanged(  )
        
    def _brightnessChanged(self) -> None:
        value = withinZeroToOne(self.__value *( self.source.brightness.value or 0.0) )
        dutyCycle = int( value * CilgerranLED.DUTY_CYCLE_RANGE )
        if dutyCycle != self.__dutyCycle:
            try:
                if self.enableDbgOut: self.dbgOut("dutyCycle changing from %s to %s", self.__dutyCycle, dutyCycle)
                # print(f"setValue {self.__pin} duty_cycle {dutyCycle}")
                self.__output.duty_cycle = dutyCycle
                self.__dutyCycle = dutyCycle
            except Exception as inst:
                self.__board.SHOW_EXCEPTION(inst, f"setValue {self.__pin} duty_cycle {dutyCycle} failed" )
        
    def getValue(self, context: Optional[UpdateContext] = None ) -> AnyRGBValue:
        return self.__value
    
    @property
    def value(self): return self.__value
    
    def __repr__(self):
        return f"Clg({self.__pin},{self.__value},{self.__output.duty_cycle})"

#############################################################################


class CilgerranPixelSource( LightSource, NamedOutputTarget, Tunable ):

    motorChannels = [6, 7]

    def __init__( self, board:"CilgerranCastle",  maxLeds:int = 8, **kwargs:Unpack[LightSource.KWDS] ) -> None:
        self.__leds:List[CilgerranLED|None] = [None] * maxLeds
        self.__sourceLeds:List[CilgerranLED] = []
        self.__maxLeds = maxLeds
        self.__brightness:ZeroToOne = 1.0
        self._motorPinsReserved: bool = False


        kwargs["lights"] = self.__sourceLeds # type: ignore

        LightSource.__init__(self, **kwargs)
        NamedOutputTarget.__init__(self, name=kwargs.get("name","CilgerranCastleLEDs") )
        Tunable.__init__(self)

        #def onChange(context:EvaluationContext, value:Any) -> None:
        #    if self.enableDbgOut: self.dbgOut("brightness changed to %.2f", value)
        #    self.__brightness = withinZeroToOne(value)
        #self.__brightnessTarget = TunableSetting[ZeroToOne]( onChange=onChange, initialValue=1.0, name="brightness")
        
        self.__board = board
        self.__LED_PINS=[ 
                        board.D5,
                        board.D6,
                        board.D7,
                        board.D8,
                        board.D4,
                        board.D3,
                        board.D1,
                        board.D2
                        ]

    @tunableZeroToOne(0.5)
    def brightness(self, 
                   #setting:TunableSetting[ZeroToOne,CilgerranPixelSource],
                   setting:TunableZeroToOneSetting[Tunable],
                   
                     context:EvaluationContext ) -> None:
        if self.enableDbgOut: self.dbgOut("brightness changed to %.2f", setting.value)
        self.setBrightness(setting.value)

  
    #@brightness.setter
    def setBrightness(self, level:ZeroToOne):
        constrained = withinZeroToOne(level)
        if self.__brightness != constrained:
            if self.enableDbgOut: self.dbgOut("brightness changing from %.2f to %.2f", self.__brightness, constrained)
            self.__brightness = constrained
            for led in self.__sourceLeds:
                led._brightnessChanged(  )

    def addLeds(self,ledCount:int ) -> List[CilgerranLED]:
        rv: list[CilgerranLED] = []
        for index in range(1,ledCount+1):
            rv.append( self.addLed(index))
        return rv
    
    def addLed(self, ledNumber:Optional[int] = None
               # , name:Optional[str] = None
                ) -> CilgerranLED:
        if ledNumber is None:
            for i, led in enumerate( self.__leds ):
                if led is None:
                    ledNumber = i + 1
                    break
            ensure( ledNumber is not None, "no remaining LEDs" )
            assert ledNumber is not None
            
        ensure( ledNumber > 0 and ledNumber <= self.__maxLeds, "invalid LED index" )
        zIndex = ledNumber - 1
        if self._motorPinsReserved:
            ensure( zIndex not in self.motorChannels, "motor pins are reserved" )

        ensure( self.__leds[zIndex] is None, "LED %r already added", ledNumber )
        rv = CilgerranLED( #name=name, 
                          index = ledNumber, 
                          pin = self.__board.asPin(self.__LED_PINS[zIndex]),
                          board = self.__board, source=self
                          )
        self.__leds[ledNumber-1] = rv
        self.__sourceLeds.append( rv )
        return rv
    
    def _reserveMotorPins(self):
        rv:list[CilgerranLED] = []
        for zIndex in self.motorChannels:
            assert self.__leds[zIndex] is None, f"motor channel {zIndex} already used"
            channel = CilgerranLED( #name=name, 
                          index = zIndex + 1, 
                          pin = self.__board.asPin(self.__LED_PINS[zIndex]),
                          board = self.__board, source=self
                          )
            
            rv.append(channel)
            self.__leds[zIndex] = channel
        self._motorPinsReserved = True
        return rv
        

    def led(self, ledIndex:int
            #, name:Optional[str] = None 
            ) -> CilgerranLED:
        ensure( ledIndex > 0 and ledIndex <= self.__maxLeds, "invalid LED index" )
        rv = self.__leds[ledIndex-1]
        if rv is None:
            return self.addLed( ledIndex ) #, name=name)
        # assert name is None or name == rv.name
        
        return rv
    
    def lightChanged(self,light:"Light") -> None: pass

#############################################################################

class CilgerranBatterMonitor(InputSource):
    VOLT_SCALE = (1.0/65535.0) * 5.0
    def __init__(self, board:"CilgerranCastle", pin:Optional[microcontroller.Pin]=None ):
        InputSource.__init__(self,name="CilgerranBatterMonitor")
        self.__input = analogio.AnalogIn( pin or board.asPin(board.A0))
        
    def getDerivedValue(self, context:EvaluationContext) -> Volts:
        return self.__input.value * CilgerranBatterMonitor.VOLT_SCALE
    
    def check(self, context:EvaluationContext ) -> None:
        v = self.getValue(context)
        if self.enableDbgOut: self.dbgOut( "battery = %.1fV", v )

#############################################################################

class CilgerranCastle(D1MiniBoardBase):
    class KWDS(D1MiniBoardBase.KWDS):
        version: NotRequired[str]
        #brightness: NotRequired[float]
        ledCount: NotRequired[int]
        withMotor: NotRequired[bool]
        monitorBattery: NotRequired[bool]
        #neoPixelPin: NotRequired[microcontroller.Pin|str]
    
    def __init__(self,
                #name=None, 
                version:Optional[str]=None,
                #brightness:Optional[float] = 1.0,
                ledCount:int|None = None,
                withMotor:bool = False,
                monitorBattery:bool = True,
                 **kwds:Unpack[D1MiniBoardBase.KWDS] ) -> None:
        
        
        super().__init__( **kwds ) # *args, name=name, refreshRate=refreshRate, **kwds )
        c = self.config
        c.updateDefaultOptions( )

        self.__ledSource = CilgerranPixelSource( self )
  
        self.__batteryMonitor = CilgerranBatterMonitor( self ) if monitorBattery else None

        self.__version = version
        #self.__brightness:float = brightness or 1.0

        self.__ledEnable = digitalio.DigitalInOut(self.asPin(self.D0))
        self.__ledEnable.direction = digitalio.Direction.OUTPUT
        self.__ledEnable.value = False
        self.__motor:DCMotorSpinner|None = None
        if withMotor: self.motor  # force motor creation
        if ledCount is not None:
            ensure( ledCount > 0, "ledCount must be greater than 0" )
            self.__ledSource.addLeds(ledCount)  

    @property
    def batteryMonitor(self) -> CilgerranBatterMonitor | None:
        return self.__batteryMonitor
    
    @property
    def ledSource(self) -> CilgerranPixelSource:
        return self.__ledSource
    
    def derivedRefresh(self, context:EvaluationContext) -> None:
        try:
            if self.__batteryMonitor is not None:
                self.__batteryMonitor.check(context)
        except Exception as inst:
            self.SHOW_EXCEPTION( inst, f"Cilgerran update exception")


    @property
    def motor(self) -> DCMotorSpinner:
        if self.__motor is None:
            motorPins = self.ledSource._reserveMotorPins()
            self.__motor = DCMotorSpinner(
                inA = motorPins[0],
                inB = motorPins[1]
            )
        return self.__motor

#############################################################################

__profileImport.complete()
