from __future__ import annotations

import neopixel 

import microcontroller

from LumensalisCP.Lights._common import *

from LumensalisCP.Lights.Groups import LightSource
    
class NeoPixelLight( RGBLight ):

    def __init__(self, source:"NeoPixelSource", index:int = 0):
        super().__init__(source=source, index=index)
        self.__npiv = 0
        

    def setValue(self,value:AnyRGBValue, context: Optional[EvaluationContext] = None ) ->None:
        if context is not None:
            value = context.valueOf(value)
        v = LightValueNeoRGB.toNeoPixelRGBInt(value)
        if v != self.__npiv:
            self.__npiv = v
            source:NeoPixelSource = self.source # type: ignore
            source.neopix[self.sourceIndex] = v # type: ignore
            source.lightChanged(self)

    def getValue(self, context: Optional[EvaluationContext] = None ) -> AnyRGBValue:
        return self.__npiv
    
    def getLightValue( self ):
        return LightValueNeoRGB( self.__npiv )
    
class  NeoPixelSourceKwds(TypedDict):
    pixelCount: NotRequired[int]
    brightness: NotRequired[float]
    pixel_order: NotRequired[str]
    #auto_write: NotRequired[bool] = False

class NeoPixelSource( LightSource ):
    """A chain of NeoPixels as a LightSource"""
    
    class KWDS( LightSource.KWDS ):
        pixelCount: NotRequired[int]
        brightness: NotRequired[float]
        pixel_order: NotRequired[str] # [neopixel.PixelOrder]
        #auto_write: NotRequired[bool] = False
        
    def __init__(self, 
            pin:microcontroller.Pin, 
            main:MainManager,
            pixelCount:int=1,
            refreshRate:float|None = 0.1,
            pixel_order:  str = neopixel.GRB,
            brightness:float = 1.0,
            #auto_write= False,
            bpp:int = 3,
            **kwds:Unpack[LightSource.KWDS] 
        ) -> None:

        self.__npLights:List[NeoPixelLight] = []
        kwds['lights'] = self.__npLights # type: ignore
        super().__init__( **kwds )
        self.neopix = neopixel.NeoPixel( pin, pixelCount, # type: ignore
                        pixel_order=pixel_order, brightness=brightness,
                        # auto_write = False
                ) #**kwds)
        
        for index in range(pixelCount):
            self.__npLights.append( NeoPixelLight( self, index) )
        assert main is not None
        assert len(self.__npLights) == pixelCount
        assert self.lightCount == pixelCount
        
        self._main = main
        self._changesSinceRefresh = 0
        self._refreshRate = refreshRate
        self._latestRefresh = 0
        self._showings = 0

    def lightChanged(self,light:Light):
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
        
        self.neopix.show() # type: ignore
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