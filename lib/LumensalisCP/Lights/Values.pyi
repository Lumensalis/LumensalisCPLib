from __future__ import annotations

from random import random as randomZeroToOne, randint
# pylint: disable=unused-argument

from LumensalisCP.IOContext import *

type RawOrEvaluatable[T] = Union[T, Evaluatable]

type rgbTuple = tuple[float,float,float]
type AnyRawLightValue = Union[
        int, float, bool,
        rgbTuple,
        # List [float],
        str, RGB
    ] 

type AnyLightValue = RawOrEvaluatable[ AnyRawLightValue]

class RGB(object):
    
    CONVERTORS = dict[type,Callable]

    def __init__(self, r:ZeroToOne|tuple|"RGB"=0, g:Optional[ZeroToOne]=None, b:Optional[ZeroToOne]=None ): ...
        
    @property 
    def r(self)->ZeroToOne: ... 
    @r.setter
    def r(self,v): ... 
    
    @property 
    def g(self)->ZeroToOne: ... 
    @g.setter
    def g(self,v): ... 
    
    @property 
    def b(self)->ZeroToOne: ... 
    @b.setter
    def b(self,v): ... 
    
    def toNeoPixelInt( self ) -> int: ... 
        
    def _set(self, r:ZeroToOne, g:ZeroToOne,b:ZeroToOne): ... 
    
    def rgbTuple(self) -> Tuple[ZeroToOne,ZeroToOne,ZeroToOne]: ...
        
    @staticmethod
    def fromNeoPixelInt( npi:int ) ->"RGB": ...
    def fadeTowards(self, other:"RGB", ratio:ZeroToOne )->"RGB": ...
    @property
    def brightness(self)->float: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...


class LightValueBase(object):
    def __init__(self, *args, **kwds): pass

    @property
    def brightness(self)->float: pass

    @property
    def asNeoPixelInt(self)->int: pass
    
    @property
    def asRGB(self) -> RGB: pass

    def setLight(self, value): pass

def registerToRGB( cf = lambda v:v) -> Callable: pass

@registerToRGB( lambda v: v )
class LightValueRGB(RGB, LightValueBase ):
    RED = RGB( 1, 0, 0 )
    BLUE = RGB( 0, 0, 1 )
    YELLOW = RGB( 0, 1, 1 )
    GREEN = RGB( 0, 1, 0 )
    BLACK = RGB( 0, 0, 0 )
    WHITE = RGB( 1, 1, 1 )
    
    @staticmethod
    def lookupColor( color:str ) ->RGB: pass

    @staticmethod
    def toRGB( value:AnyLightValue )->RGB:pass

    @staticmethod
    def prepRGBValue( value:AnyLightValue ) ->RGB: pass
        
    def setLight(self, value:AnyLightValue): pass

    @staticmethod
    def randomRGB( brightness:ZeroToOne=1) -> RGB: pass

    @property
    def asNeoPixelInt(self)->int: pass
    
    @property
    def asRGB(self) -> RGB: pass
    
@registerToRGB( lambda v: v )
class LightValueNeoRGB(LightValueBase):
    __slots__ = "_LightValueNeoRGB__brightness", "_LightValueNeoRGB__value"

    
    @staticmethod
    def toNeoPixelInt( value:AnyLightValue )->int: pass
    
    @staticmethod
    def formatNeoRGBValues( values ) ->str: pass
    
    def __init__(self,  value:AnyLightValue ): pass

    @staticmethod
    def randomRGB( brightness:ZeroToOne=1) ->int: pass

    @property
    def brightness(self)->float: pass
    
    def setLight(self, value:AnyLightValue): pass

    @property
    def asNeoPixelInt(self)->int: pass
    
    @property
    def asRGB(self) -> RGB: pass


#############################################################################
def wheel255( val:float ): ...

def wheel1( val:float ): ...
