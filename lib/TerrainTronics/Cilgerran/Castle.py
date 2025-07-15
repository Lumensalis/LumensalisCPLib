
import TerrainTronics.D1MiniBoardBase
from LumensalisCP.IOContext import *
from LumensalisCP.commonCP import *
from LumensalisCP.Triggers.Timer import PeriodicTimer
from LumensalisCP.Lights.Light import *


class CilgerranLED( DimmableLight ):
    # source : ( CilgerranPixelSource )

    PWM_FREQUENCY = 2000
    
    DUTY_CYCLE_RANGE = 65535
    def __init__(self, name, board:"CilgerranCastle", index:int, pin=None, **kwargs ):
        super().__init__( name=name, **kwargs )
        #print(f'CilgerranLED {name} [{index}]')
        #self.__board:"CilgerranCastle" = board
        self.__main = board.main
        self.__index = index
        self.__value = 0
        self.__output = pwmio.PWMOut(pin=board.asPin(pin), frequency= CilgerranLED.PWM_FREQUENCY,duty_cycle=0 ) 
        

    def setValue(self,value:AnyLightValue, context: UpdateContext = None ):
        context = context or self.__main.latestContext
        level = toZeroToOne(context.valueOf( value ) )
        self.__value = value
        self.__output.duty_cycle = int( value * self.source.brightness * CilgerranLED.DUTY_CYCLE_RANGE )
    
    def _brightnessChanged(self):
        self.__output.duty_cycle = int( self.__value * self.source.brightness * CilgerranLED.DUTY_CYCLE_RANGE )

    @overload
    def getValue(self, context: UpdateContext = None ) -> AnyLightValue:
        return self.__value
    
    @property
    def value(self): return self.__value
    
    def __repr__(self):
        return f"CilgerranLED( {self.name}, {self.__index}, v={self.__value}, dc={self.__output.duty_cycle} )"


class CilgerranPixelSource( LightSource, NamedOutputTarget ):

    def __init__( self, board:"CilgerranCastle", name:str|None=None, maxLeds = 8, **kwargs ):
        self.__leds:List[CilgerranLED] = [None] * maxLeds
        self.__maxLeds = maxLeds

        LightSource.__init__(self, name=name, lights = self.__leds, **kwargs)
        NamedOutputTarget.__init__(self, name=name)

  
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

    @property
    def brightness(self): return self.__brightness

    @brightness.setter
    def brightness(self, level:float):
        level = toZeroToOne(level)
        self.__brightness = max(0.0, min( 1.0, level ) )
        for led in self.__leds:
            if led is not None:
                led._brightnessChanged(  )

    def addLeds(self,ledCount:int|str, **names:str ) -> List[CilgerranLED]:
        rv = []
        if type(ledCount) is str:
            rv.append( self.addLed(name=ledCount))
        else:
            for index in range(1,ledCount+1):
                rv.append( self.addLed(index))
        for name in names:
            rv.append( self.addLed(name=name))
        return rv
    
    def addLed(self, ledNumber:int|None = None, name:str = None ) -> CilgerranLED:
        if ledNumber is None:
            for i, led in enumerate( self.__leds ):
                if led is None:
                    ledNumber = i + 1
                    break
            ensure( ledNumber is not None, "no remaining LEDs" )
            
        ensure( ledNumber > 0 and ledNumber <= self.__maxLeds, "invalid LED index" )
        zIndex = ledNumber - 1
        ensure( self.__leds[zIndex] is None, "LED %r already added", ledNumber )
        rv = CilgerranLED( name=name, index = ledNumber, 
                          pin = self.__board.asPin(self.__LED_PINS[zIndex]),
                          board = self.__board, source=self
                          )
        self.__leds[ledNumber-1] = rv
        return rv

    def led(self, ledIndex:int, name:str = None ) -> CilgerranLED:
        ensure( ledIndex > 0 and ledIndex <= self.__maxLeds, "invalid LED index" )
        rv = self.__leds[ledIndex-1]
        if rv is None:
            return self.addLed( ledIndex, name=name)
        assert name is None or name == rv.name
        
        return rv
    
    def lightChanged(self,light:"Light"): pass
        
class CilgerranBatterMonitor(InputSource):
    VOLT_SCALE = (1.0/65535.0) * 5.0
    def __init__(self, board:"CilgerranCastle", pin=None ):
        InputSource.__init__(self,name="CilgerranBatterMonitor")
        self.__input = analogio.AnalogIn( board.asPin(board.A0))
        
    def getDerivedValue(self, context:EvaluationContext) -> Volts:
        return self.__input.value * CilgerranBatterMonitor.VOLT_SCALE
    
    def check(self, context:EvaluationContext ):
        v = self.getValue(context)
        self.enableDbgOut and self.dbgOut( "battery = %.1fV", v )

    
class CilgerranCastle(TerrainTronics.D1MiniBoardBase.D1MiniBoardBase):
    
    def __init__(self, *args,
                name=None, 
                version:str=None,
                brightness = 1.0,
                refreshRate=0.001,
                ledCount:int|None = None,
                withMotor:bool = False,
                monitorBattery:bool = True,
                 **kwds ):
        
        name = name or "Cilgerran"
        super().__init__( *args, name=name, refreshRate=refreshRate, **kwds )
        c = self.config
        c.updateDefaultOptions( )

        self.__ledSource = CilgerranPixelSource( self )
  
        self.__batteryMonitor = CilgerranBatterMonitor( self ) if monitorBattery else None

        self.__version = version

        self.__brightness:float = 1.0

        self.__ledEnable = digitalio.DigitalInOut(self.asPin(self.D0))
        self.__ledEnable.direction = digitalio.Direction.OUTPUT
        self.__ledEnable.value = 0

    @property
    def batteryMonitor(self): return self.__batteryMonitor
    
    @property
    def ledSource(self) -> CilgerranPixelSource: return self.__ledSource
    
    def doRefresh(self, context):
        try:
            self.__batteryMonitor.check(context)
        except Exception as inst:
            print( f"Cilgerran update exception {inst}")




