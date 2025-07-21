
from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.I2C.I2CDevice import I2CDevice, I2CInputSource, UpdateContext
from LumensalisCP.Lights.Light import *


from .aw210xx import AW210xx, AW210xxOpenShortDetect


class HarlechXL_LED( DimmableLight ):
    # source : ( CilgerranPixelSource )

    PWM_FREQUENCY = 20000
    DUTY_CYCLE_RANGE = 65535
    
    def __init__(self, name, source:"HarlechXLCastle", index:int, pin=None, **kwargs ):
        super().__init__( name=name, source=source,**kwargs )
        self.__index = index
        self.__driver = source._ledDriver
        self.__value = 0
        
    @property
    def _driverValue(self):
        raw = self.__value * self.source.brightness*255
        v255 =  int(max(0,min(raw,255)))
        return v255
    
    def setValue(self,value:AnyLightValue, context: UpdateContext = None ):
        level = toZeroToOne(context.valueOf( value ) )
        self.__value = value
        
        self.__driver.br( self.__index, self._driverValue )
        self.source.lightChanged(self)
    
    def _brightnessChanged(self):
        self.__driver.br( self.__index, self._driverValue )

    def getValue(self, context: UpdateContext = None ) -> AnyLightValue:
        return self.__value
    
    def __repr__(self):
        return f"CilgerranLED( {self.name}, {self.__index}, v={self.__value} )"


class HarlechXLCastle(I2CDevice, LightSource ):

    def __init__( self, name:str|None =None, 
                 maxLeds = 32,
                 address=0x34,
                 updateInterval = 0.1,
                 **kwargs ):
        
        name = name or "HarlechXLCastle"
        self.__leds:List[HarlechXL_LED] = [None] * maxLeds
        self.__maxLeds = maxLeds
        self.__brightness = 1.0
        self.__ledChanges = 0

        super().__init__(address=address, updateInterval=updateInterval, **kwargs)
        LightSource.__init__(self, name=name, lights= self.__leds ),


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
    def brightness(self): return self.__brightness

    @brightness.setter
    def brightness(self, level:float):
        level = toZeroToOne(level)
        self.__brightness = max(0.0, min( 1.0, level ) )
        for led in self.__leds:
            if led is not None:
                led._brightnessChanged(  )

    def addLeds(self,ledCount:int|str, **names:str ) -> List[HarlechXL_LED]:
        rv = []
        if type(ledCount) is str:
            rv.append( self.addLed(name=ledCount))
        else:
            for index in range(ledCount):
                rv.append( self.addLed(index))
        for name in names:
            rv.append( self.addLed(name=name))
        return rv
    
    
    def addLed(self, ledNumber:int|None = None, name:str = None ) -> HarlechXL_LED:
        #self.infoOut("addLed %r %r", ledNumber,  None )
        if ledNumber is None:
            for i, led in enumerate( self.__leds ):
                if led is None:
                    ledNumber = i
                    break
            ensure( ledNumber is not None, "no remaining LEDs" )
            
        ensure( ledNumber >= 0 and ledNumber < self.__maxLeds, "invalid LED index" )
        # zIndex = ledNumber 
        ensure( self.__leds[ledNumber] is None, "LED %r already added", ledNumber )
        rv = HarlechXL_LED( name=name, index = ledNumber, source=self )
        self.__leds[ledNumber] = rv
        return rv

    def led(self, ledIndex:int, name:str = None ) -> HarlechXL_LED:
        ensure( ledIndex >= 0 and ledIndex < self.__maxLeds, "invalid LED index" )
        rv = self.__leds[ledIndex]
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

        faults = []
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


    def derivedUpdateDevice(self, context:EvaluationContext):
        #self.infoOut( "derivedUpdateDevice changed=%r", self.__ledChanges )
        self.__ledChanges = 0
        self._ledDriver.update()
