from .LightBase import *
from LumensalisCP.Main.Manager import MainManager
import neopixel

#import adafruit_led_animation.animation.blink
#import adafruit_led_animation.helper


class NeoPixelLight( RGBLightBase ):

    def __init__(self, source:"NeoPixelSource", index:int = 0):
        super().__init__(source=source, index=index)
        self.__npiv = 0
        
    def setValue(self,value:AnyLightValue, context: UpdateContext = None ):
        v = LightValueNeoRGB.toNeoPixelInt(value)
        if v != self.__npiv:
            self.__npiv = v
            source:"NeoPixelSource" = self.source
            source.neopix[self.sourceIndex] = v
            source.lightChanged(self)

class NeoPixelSource( LightSourceBase ):
    def __init__(self, pin, pixelCount:int, name:str=None, refreshRate:int = 0, main:MainManager = None, **kwds):
        self.__npLights:List[NeoPixelLight] = []
        super().__init__( lights = self.__npLights, name=name or f"{self.__class__.__name__}_{pin}" )
        self.neopix = neopixel.NeoPixel( pin, pixelCount,**kwds)
        for index in range(pixelCount):
            self.__npLights.append( NeoPixelLight( self, index) )
        self._main = main
        self._changesSinceRefresh = 0
        self._refreshRate = refreshRate
        self._latestRefresh = 0

    def lightChanged(self,light:LightBase):
        self._changesSinceRefresh += 1
        
    if 0:
        # old override to catch change when this inherited from neopixel.NeoPixel
        def _set_item(
            self, index: int, r: int, g: int, b: int, w: int
        ):  # pylint: disable=too-many-locals,too-many-branches,too-many-arguments
            if index < 0:
                index += len(self)
            if index >= self._pixels or index < 0:
                raise IndexError
            offset = self._offset + (index * self._bpp)
            contentsBefore = self._pre_brightness_buffer[offset,  self._bpp]
            super()._set_item( index, r, g, b, w )
            contentsAfter = self._pre_brightness_buffer[offset,  self._bpp]
            if contentsAfter != contentsBefore:
                self._changesSinceRefresh += 1

    def refresh(self):
        if self._refreshRate:
            elapsed = self._main.when - self._latestRefresh
            if elapsed > self._refreshRate:
                self.show()

    def show(self):
        #super().show()
        self.neopix.show()
        self._latestRefresh = self._main.when
        