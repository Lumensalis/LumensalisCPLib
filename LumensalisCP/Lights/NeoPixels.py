from .LightBase import *
from LumensalisCP.Main.Manager import MainManager
import neopixel

from LumensalisCP.util.bags import Bag

#import adafruit_led_animation.animation.blink
#import adafruit_led_animation.helper

class NeoPixelLight( RGBLightBase ):

    def __init__(self, source:"NeoPixelSource", index:int = 0):
        super().__init__(source=source, index=index)
        self.__npiv = 0
        
    def setValue(self,value:AnyLightValue, context: UpdateContext = None ):
        if context is not None:
            value = context.valueOf(value)
        v = LightValueNeoRGB.toNeoPixelInt(value)
        if v != self.__npiv:
            self.__npiv = v
            source:"NeoPixelSource" = self.source
            source.neopix[self.sourceIndex] = v
            source.lightChanged(self)

    def getValue(self, context: UpdateContext = None ) -> AnyLightValue:
        return self.__npiv
    
    def getLightValue( self ):
        return LightValueNeoRGB( self.__npiv )
    
class NeoPixelSource( LightSourceBase ):
    def __init__(self, pin, pixelCount:int, name:str=None, refreshRate:float|None = 0.1, main:MainManager = None, **kwds):
        self.__npLights:List[NeoPixelLight] = []
        super().__init__( lights = self.__npLights, name=name or f"{self.__class__.__name__}_{pin}" )
        self.neopix = neopixel.NeoPixel( pin, pixelCount,**kwds)
        for index in range(pixelCount):
            self.__npLights.append( NeoPixelLight( self, index) )
        self._main = main
        self._changesSinceRefresh = 0
        self._refreshRate = refreshRate
        self._latestRefresh = 0
        self._showings = 0

    def lightChanged(self,light:LightBase):
        self._changesSinceRefresh += 1
        
    @property
    def refreshRate(self) -> float|None: return self._refreshRate
    
    @refreshRate.setter
    def refreshRate(self, rr:float|None):
        self._refreshRate = rr
        
    def refresh(self):
        if self._refreshRate is not None:
            elapsed = self._main.when - self._latestRefresh
            if elapsed > self._refreshRate:
                if self._changesSinceRefresh:
                    self.show()

    def show(self):
        #super().show()
        
        self.neopix.show()
        self._showings += 1
        self._changesSinceRefresh = 0
        self._latestRefresh = self._main.when
    
        
    def stats(self)->Bag:
        return Bag(
                    showings = self._showings, 
                    latestRefresh = self._latestRefresh,
                    refreshRate = self._refreshRate,
                    changesSinceRefresh = self._changesSinceRefresh, 
                     # = self.__step, 
                    
        )