from __future__ import annotations
from random import random as randomZeroToOne, randint
from collections import namedtuple
import rainbowio 

from LumensalisCP.common import *
from LumensalisCP.Eval.Evaluatable import Evaluatable
from LumensalisCP.Lights.RGB import RGB, AnyRGBValue, registerToRGB


def wheel255( val:float ): return rainbowio.colorwheel(val)

def wheel1( val:float ): return rainbowio.colorwheel(val*255.0)

#############################################################################

#############################################################################

class LightValueBase(object):
    def __init__(self, *args, **kwds):
        pass

    @property
    def brightness(self)->float: raise NotImplementedError

    @property
    def asNeoPixelRGBInt(self)->int: raise NotImplementedError
    
    @property
    def asRGB(self) -> RGB: raise NotImplementedError

    def setLight(self, value) ->None: raise NotImplementedError


#############################################################################

@registerToRGB( lambda v: v )
class LightValueRGB(RGB, LightValueBase ):


    @staticmethod
    def prepRGBValue( value ):
        if (
                isinstance( value, Evaluatable ) or
                callable(value)
        ):
            return value
        
        return RGB.toRGB( value )
        
    def setLight(self, value):
        v = RGB.toRGB( value )
        self._set( *v.rgbTuple() )

    @staticmethod
    def randomRGB( brightness:ZeroToOne=1) -> RGB:
        return RGB( randomZeroToOne() * brightness,  randomZeroToOne() * brightness,  randomZeroToOne() * brightness )

    @property
    def asNeoPixelRGBInt(self)->int: 
        return self.toNeoPixelRGBInt()
    
    @property
    def asRGB(self) -> RGB:
        return RGB( self.rgbTuple() )

#############################################################################

@registerToRGB( lambda v: v )
class LightValueNeoRGB(LightValueBase):
    __slots__ = "_LightValueNeoRGB__brightness", "_LightValueNeoRGB__value"

    NP_INT_CONVERTORS = dict(
        int= lambda v:v & 0xFFFFFF,
        float= lambda v: ( b255 := max(0,min(255,int(v * 255))), b255 + (b255 << 8) + (b255 << 16) )[1],
        bool= lambda v: 0xFFFFFF if v else 0,
        tuple= lambda v: (max(0,min(255,int(v[0]))) << 16) + (max(0,min(255,int(v[1]))) << 8) + (max(0,min(255,int(v[2])))),
        list= lambda v: (max(0,min(255,int(v[0]))) << 16) + (max(0,min(255,int(v[1]))) << 8) + (max(0,min(255,int(v[2])))),
        
    )
    @staticmethod
    def toNeoPixelRGBInt( value:AnyRGBValue )->int:
        convertor = LightValueNeoRGB.NP_INT_CONVERTORS.get(type(value).__name__,None)
        if convertor is not None:
            return convertor(value)

        if isinstance( value, LightValueBase):
            return value.asNeoPixelRGBInt
        elif isinstance( value, RGB ):
            return value.toNeoPixelRGBInt()
        
        assert False,  safeFmt("cannot convert %r (%s) to NeoRGB", value, type(value))
    
    
    @staticmethod
    def formatNeoRGBValues( values ):
        return '|'.join( [('%6.6X'%LightValueNeoRGB.toNeoPixelRGBInt(v)) for v in values])
    
    def __init__(self,  value:AnyRGBValue ):
        self.__value = LightValueNeoRGB.toNeoPixelRGBInt( value )
        self.__brightness = 1.0

    @staticmethod
    def randomRGB( brightness:ZeroToOne=1):
        def rChannel(): return randint(0,int(255*brightness))
        return (rChannel() << 16) + (rChannel() << 8) +  rChannel()

    @property
    def brightness(self)->float: return self.__brightness
    
    def setLight(self, value):
        self.__value = LightValueNeoRGB.toNeoPixelRGBInt( value )

    @property
    def asNeoPixelRGBInt(self)->int: return self.__value
    
    @property
    def asRGB(self) -> RGB:
        return RGB.fromNeoPixelRGBInt( self.__value )

#############################################################################
# RGB.CONVERTORS[RGB.__class__.__name__] = lambda v:v
RGB.CONVERTORS[RGB] = lambda v:v
RGB.CONVERTORS[int] = RGB.fromNeoPixelRGBInt
RGB.CONVERTORS[str] = LightValueRGB.lookupColor
