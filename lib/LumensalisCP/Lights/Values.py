from __future__ import annotations
from random import random as randomZeroToOne, randint
import rainbowio 

from LumensalisCP.common import *
from LumensalisCP.Lights.RGB import *

from LumensalisCP.Eval.Evaluatable import Evaluatable
from LumensalisCP.util.Convertor import Convertor

def wheel255( val:float ): return rainbowio.colorwheel(val)

def wheel1( val:float ): return rainbowio.colorwheel(val*255.0)

#############################################################################

#############################################################################

class LightValueBase(CountedInstance):
    def __init__(self):
        super().__init__()
        

    @property
    def brightness(self)->float: raise NotImplementedError

    #@property
    #def asNeoPixelRGBInt(self)->int: raise NotImplementedError
    
    @property
    def asRGB(self) -> RGB: raise NotImplementedError

    def setLight(self, value:AnyRGBValue) ->None: 
        raise NotImplementedError


#############################################################################

@RGB.Convertors.registerChildClass()
class LightValueRGB(RGB, LightValueBase ):


    @staticmethod
    def prepRGBValue( value:AnyRGBValue |Evaluatable[RGB]) -> RGB|Evaluatable[RGB]:
        if (
                isinstance( value, Evaluatable ) or
                callable(value)
        ):
            return value # type: ignore

        return RGB.toRGB( value )
        
    def setLight(self, value:AnyRGBValue) -> None:
        v = RGB.toRGB( value )
        self._set_r_g_b( *v.rgbTuple() ) # pyright: ignore[reportPrivateUsage]

    @staticmethod
    def randomRGB( brightness:ZeroToOne=1) -> RGB:
        return RGB( randomZeroToOne() * brightness,  randomZeroToOne() * brightness,  randomZeroToOne() * brightness )

    #@property
    #def asNeoPixelRGBInt(self)->int: 
    #    return self.toNeoPixelRGBInt()
    
    @property
    def asRGB(self) -> RGB:
        return RGB( self.rgbTuple() )

#############################################################################

#@RGB.Convertors.registerChildClass()
class LightValueNeoRGB(LightValueBase):


    NeoPixelIntConvertors:ClassVar[Convertor[AnyRGBValue,NeoPixelRGBInt]] 
    NeoPixelIntConvertors = Convertor()
    
    @staticmethod
    def toNeoPixelRGBInt( value:AnyRGBValue )->NeoPixelRGBInt:
        return LightValueNeoRGB.NeoPixelIntConvertors(value) # type: ignore
    
        convertor = LightValueNeoRGB.NeoPixelIntConvertors.get(type(value).__name__,None)
        if convertor is not None:
            return convertor(value)

        if isinstance( value, LightValueBase):
            return value.asNeoPixelRGBInt
        elif isinstance( value, RGB ):
            return value.asNeoPixelRGBInt()
        
        assert False,  safeFmt("cannot convert %r (%s) to NeoRGB", value, type(value))
    
    
    @staticmethod
    def formatNeoRGBValues( values:list[AnyRGBValue] ) ->str:
        asRGBInts = [LightValueNeoRGB.toNeoPixelRGBInt(v) for v in values]
        return '|'.join( [('%6.6X'%v) for v in asRGBInts])
    
    def __init__(self,  value:AnyRGBValue ):
        self.__value = self.toNeoPixelRGBInt( value )
        self.__brightness = 1.0

    @staticmethod
    def randomRGB( brightness:ZeroToOne=1):
        def rChannel(): return randint(0,int(255*brightness))
        return (rChannel() << 16) + (rChannel() << 8) +  rChannel()

    @property
    def brightness(self)->float: return self.__brightness
    
    def setLight(self, value:AnyRGBValue) -> None:
        self.__value = self.toNeoPixelRGBInt( value )

    #@property
    #def asNeoPixelRGBInt(self)->int: return self.__value
    
    @property
    def asRGB(self) -> RGB:
        return RGB.fromNeoPixelRGBInt( self.__value )

#############################################################################
# Colors.CONVERTORS[RGB.__class__.__name__] = lambda v:v
#Colors.CONVERTORS[RGB] = lambda v:v
#Colors.CONVERTORS[int] = RGB.fromNeoPixelRGBInt
#Colors.CONVERTORS[str] = LightValueRGB.lookupColor

@LightValueNeoRGB.NeoPixelIntConvertors.defineRegisterConvertor( int )
def intToNeoRGBInt( v:int ) -> NeoPixelRGBInt: 
    return  NeoPixelRGBInt(v & 0xFFFFFF)

@LightValueNeoRGB.NeoPixelIntConvertors.defineRegisterConvertor( float ) 
def floatToNeoRGBInt( v:float ) -> NeoPixelRGBInt:
    b255 = max(0, min(255, int(v * 255)))
    return NeoPixelRGBInt(b255 + (b255 << 8) + (b255 << 16))

@LightValueNeoRGB.NeoPixelIntConvertors.defineRegisterConvertor( bool )
def boolToNeoRGBInt( v:bool ) -> NeoPixelRGBInt:
    return NeoPixelRGBInt(0xFFFFFF if v else 0)

@LightValueNeoRGB.NeoPixelIntConvertors.defineRegisterConvertor( tuple )
def tupleToNeoRGBInt( v:tuple[float,float,float] ) -> NeoPixelRGBInt:
    return NeoPixelRGBInt(  (max(0, min(255, int(v[0]))) << 16) +
                            (max(0, min(255, int(v[1]))) << 8) +
                            (max(0, min(255, int(v[2])))) ) 

@LightValueNeoRGB.NeoPixelIntConvertors.defineRegisterConvertor( list )
def listToNeoRGBInt( v:list[float] ) -> NeoPixelRGBInt:
    return NeoPixelRGBInt(  (max(0, min(255, int(v[0]))) << 16) +
                            (max(0, min(255, int(v[1]))) << 8) +
                            (max(0, min(255, int(v[2])))) )     

@LightValueNeoRGB.NeoPixelIntConvertors.defineRegisterConvertor( RGB )
def _( v:RGB ) -> NeoPixelRGBInt:
    return v.asNeoPixelRGBInt()

#        {
            #int: lambda v:v & 0xFFFFFF,
#            float: lambda v: ( b255 := max(0,min(255,int(v * 255))), b255 + (b255 << 8) + (b255 << 16) )[1],
#            bool= lambda v: 0xFFFFFF if v else 0,
#            tuple= lambda v: (max(0,min(255,int(v[0]))) << 16) + (max(0,min(255,int(v[1]))) << 8) + (max(0,min(255,int(v[2])))),
#            list= lambda v: (max(0,min(255,int(v[0]))) << 16) + (max(0,min(255,int(v[1]))) << 8) + (max(0,min(255,int(v[2])))),
#        }
#    )

__all__ = [
    'LightValueBase',
    'LightValueNeoRGB',
    'wheel255',
    'wheel1',
]