
from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.I2C.I2CDevice import I2CDevice, UpdateContext
from LumensalisCP.Lights.Light import *

# pyright: reportPrivateUsage=false

from TerrainTronics.HarlechXL.aw210xx import AW210xx, AW210xxOpenShortDetect
from lumensaliscplib.lib.LumensalisCP.Eval.EvaluationContext import EvaluationContext


class HarlechXL_LED( DimmableLight ):
    # source : ( CilgerranPixelSource )

    PWM_FREQUENCY = 20000
    DUTY_CYCLE_RANGE = 65535

    def __init__(self,   **kwargs:Unpack[DimmableLight.KWDS]) -> None:
        super().__init__( **kwargs )
        
        assert isinstance(self.source, HarlechXLCastle)
        self.__driver = self.source._ledDriver
        self.__value:AnyRGBValue = 0
        
    @property
    def _driverValue(self) -> int:
        raw = self.__value * self.source.brightness*255 # type: ignore
        v255 =  int(max(0,min(raw,255))) # type: ignore
        return v255
    
    def setValue(self,value:AnyRGBValue, context: Optional[UpdateContext] = None ) -> None:
        #level = toZeroToOne(context.valueOf( value ) )
        self.__value = value
        
        self.__driver.br( self.sourceIndex, self._driverValue )
        self.source.lightChanged(self)
    
    def _brightnessChanged(self):
        self.__driver.br( self.sourceIndex, self._driverValue )

    def getValue(self, context: Optional[EvaluationContext] = None ) -> AnyRGBValue:
        return self.__value
    
    def __repr__(self):
        return f"CilgerranLED( {self.name}, {self.sourceIndex}, v={self.__value} )"


class HarlechXLCastle(I2CDevice, LightSource ):

    class KWDS(I2CDevice.KWDS, LightSource.KWDS):
        pass
    def __init__( self, name:str|None =None, 
                 maxLeds:int = 32,
                 address:int=0x34,
                 refreshRate:TimeSpanInSecondsConfigArg = 0.1,
                 **kwargs:Any ):
        
        name = name or "HarlechXLCastle"
        self.__fixedLeds:list[HarlechXL_LED|None] = [None] * maxLeds
        self.__createdLeds:list[HarlechXL_LED] = []
        self.__maxLeds = maxLeds
        self.__brightness = 1.0
        self.__ledChanges = 0

        super().__init__(address=address, refreshRate=refreshRate, **kwargs)
        LightSource.__init__(self, name=name, lights= self.__createdLeds )


        self._ledDriver = AW210xx( self.i2c,r_ext=3650, model="AW21036", address=address)
        
        self._ledDriver.reset()
        self._ledDriver.chip_enabled(True)
        
        self.infoOut("Driver ID: 0x%02X, Driver Version: 0x%02X",
                     self._ledDriver.get_id(), self._ledDriver.get_version()
                    )
        self._ledDriver.global_current(255)
        self.infoOut("%d leds, Maximum current per channel is %r", maxLeds, self._ledDriver.max_global_current())
        for i in range(maxLeds):
            self._ledDriver.col(i,255)
        self.addLeds(maxLeds)

    @property
    def brightness(self) -> float: return self.__brightness

    @brightness.setter
    def brightness(self, level:float):
        level = toZeroToOne(level)
        self.__brightness = max(0.0, min( 1.0, level ) )
        for led in self.__fixedLeds:
            if led is not None:
                led._brightnessChanged(  )

    def addLeds(self,ledCount:int|str, **names:str ) -> List[HarlechXL_LED]:
        rv:list[HarlechXL_LED] = []
        if isinstance(ledCount, str):
            rv.append( self.addLed(name=ledCount))
        else:
            for index in range(ledCount):
                rv.append( self.addLed(index))
        for name in names:
            rv.append( self.addLed(name=name))
        return rv
    
    
    def addLed(self, ledNumber:Optional[int] = None, name:Optional[str] = None ) -> HarlechXL_LED:
        #self.infoOut("addLed %r %r", ledNumber,  None )
        if ledNumber is None:
            for i, led in enumerate( self.__fixedLeds ):
                if led is None:
                    ledNumber = i
                    break
            assert ledNumber is not None, "no remaining LEDs" 
            
        ensure( ledNumber >= 0 and ledNumber < self.__maxLeds, "invalid LED index" )
        # zIndex = ledNumber 
        ensure( self.__fixedLeds[ledNumber] is None, "LED %r already added", ledNumber )
        rv = HarlechXL_LED(  index = ledNumber, source=self,name=name or f"LED{ledNumber}" )
        self.__fixedLeds[ledNumber] = rv
        return rv

    def led(self, ledIndex:int, name:Optional[str] = None ) -> HarlechXL_LED:
        assert  ledIndex >= 0 and ledIndex < self.__maxLeds, "invalid LED index" 
        rv = self.__fixedLeds[ledIndex]
        if rv is None:
            return self.addLed( ledIndex, name=name)
        assert name is None or name == rv.name
        
        return rv
    
    def lightChanged(self,light:"Light"): 
        self.__ledChanges += 1
    
    
    def _parse_openshort(self, leds: AW210xx, display_name: str) -> None:
        results = leds.get_open_short_status()
        if results == 0:
            print(f"{display_name}: no faults detected")
            return

        faults:list[Any] = []
        for i in range(leds.NUM_CHANNELS):
            if results & (1 << i) != 0:
                faults.append(i)

        print(f"{display_name}: faults on channels {faults} detected")


    def checkOpenShort(self):
        leds = self._ledDriver
        assert leds.chip_enabled()

        # Set all LEDs to consume 1mA as recommended in datasheet
        global_current_max = int(0.001 / leds.max_current() * 255)
        leds.global_current(global_current_max)
        print(f"Set LED current to {leds.max_global_current() * 1000:.3f}mA")
        for i in range(leds.NUM_CHANNELS):
            leds.col(i, 255)
            leds.br(i, 255)
        leds.update()
        self._ledDriver.open_short_detect(AW210xxOpenShortDetect.OPEN_ENABLE)
        self._parse_openshort(self._ledDriver, "Open results")
        self._ledDriver.open_short_detect(AW210xxOpenShortDetect.SHORT_ENABLE)
        self._parse_openshort(self._ledDriver, "Short results")


    def derivedUpdateDevice(self, context:EvaluationContext) -> bool:
        #self.infoOut( "derivedUpdateDevice changed=%r", self.__ledChanges )
        self.__ledChanges = 0
        self._ledDriver.update()
        return self.__ledChanges > 0