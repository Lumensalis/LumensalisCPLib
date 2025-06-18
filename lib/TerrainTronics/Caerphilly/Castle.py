
import TerrainTronics.D1MiniBoardBase
from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
#from LumensalisCP.Lights.LightBase import *
from LumensalisCP.Main.Updates import Refreshable, UpdateContext
import neopixel
from LumensalisCP.Lights.NeoPixels import NeoPixelSource

from LumensalisCP.Gadgets.IrRemote import LCP_IRrecv, onIRCode

import LumensalisCP.Main.Expressions

class CaerphillyCastle(TerrainTronics.D1MiniBoardBase.D1MiniBoardBase):
    
    def __init__(self, *args, name=None, **kwds ):
        name = name or "Caerphilly"
        super().__init__( *args, name=name, **kwds )
        c = self.config
        c.updateDefaultOptions( 
                neoPixelPin = c.D3,
                neoPixelCount = 1,
                neoPixelOrder = neopixel.GRB,
                neoPixelBrightness = 0.2,
                servos = 0,
                servo1pin =  c.D6,
                servo2pin =  c.D7,
                servo3pin =  c.D8,
            )
        self._irRemote = None
        self.initI2C()
        self.__pixels:NeoPixelSource = NeoPixelSource(
            c.neoPixelPin, c.neoPixelCount, main = self.main, refreshRate=0.05, brightness=c.neoPixelBrightness, auto_write=False, pixel_order=c.neoPixelOrder
        )
        self.__servos = [ None, None, None ]
        self.__neoPixOnServos = [ None, None, None ]
        self.__allPixels = [self.__pixels]
        
    def doRefresh(self,context:UpdateContext):
        for pixels in self.__allPixels:
            pixels.refresh()
        
    
    @property
    def pixels(self) -> NeoPixelSource: return self.__pixels
        
    
    def initNeoPixOnServo( self, servoN:int, 
                neoPixelCount:int = 1,
                name:str = None, 
                neoPixelOrder = neopixel.GRB,
                neoPixelBrightness = 0.2,
             ) -> NeoPixelSource:
        assert( self.__servos[servoN-1] is None  and self.__neoPixOnServos[servoN-1] is None )
        pin = self.config.option('servo{}pin'.format(servoN))
        name = name or f"pixel{servoN}"

        pixels = NeoPixelSource(
            pin, neoPixelCount, main = self.main, refreshRate=0.05,
                brightness=neoPixelBrightness, auto_write=False, pixel_order=neoPixelOrder
        )
        self.__neoPixOnServos[servoN-1] = pixels
        self.__allPixels.append(pixels)
        return pixels
    

    def addIrRemote(self, codenames:Mapping|str|None = None) -> LCP_IRrecv:
        assert self._irRemote is None
        codenames = codenames or "ar_mp3"
        self._irRemote = LCP_IRrecv( self.D5.actualPin, codenames=codenames, main=self.main )
        return self._irRemote
    
    def analogInput( self, name:str ):
        return self.A0.addAnalogInput( name=name )
