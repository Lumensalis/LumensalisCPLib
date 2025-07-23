from __future__ import annotations


#############################################################################

from random import random as randomZeroToOne, randint
import re

from LumensalisCP.common import TypeAlias, ZeroToOne,Union, Type, Callable, Optional,  Any, Tuple, NewType, ClassVar
from LumensalisCP.common import withinZeroToOne_, safeFmt
#from LumensalisCP.Eval.Evaluatable import Evaluatable, evaluate

#from LumensalisCP.CPTyping import *

RGBChannel:TypeAlias = ZeroToOne

RGBTuple:TypeAlias = Tuple[RGBChannel,RGBChannel,RGBChannel]


#############################################################################
NeoPixelRGBInt = NewType('NeoPixelRGBInt', int)

class RGB(object):
    # __slots__ = [ '_r', '_g', '_b' ]
    

    
    def __init__(self, r:RGBChannel|tuple|RGB=0.0, g:Optional[RGBChannel]=None, b:Optional[RGBChannel]=None ):
        super().__init__()
        if g is None:
            assert isinstance( b, type(None)), "b must also be None"
            if isinstance(r,str):
                c = RGB.lookupColor(r)
                assert c is not None, safeFmt("unknown color %r", r)
                r, g, b = c.r, c.g, c.b
            elif isinstance(r, (list, tuple)):
                r, b, g = r
            elif isinstance(r,RGB):
                r, b, g = r.r, r.b, r.g
            elif r is None: # type: ignore
                r,g,b = 0.0,0.0,0.0
            else:
                raise TypeError("Invalid type for RGB initialization") 
            
        self._r:RGBChannel =  withinZeroToOne_( r )
        self._g:RGBChannel =  withinZeroToOne_( g )
        self._b:RGBChannel =  withinZeroToOne_( b )
        
    @property 
    def r(self)->RGBChannel: return self._r
    @r.setter
    def r(self,v:RGBChannel): self._r = max(0.0, min(1.0,v) )
    
    @property 
    def g(self)->RGBChannel: return self._g
    @g.setter
    def g(self,v:RGBChannel): self._g = max(0.0, min(1.0,v) )
    
    @property 
    def b(self)->RGBChannel: return self._b
    @b.setter
    def b(self,v:RGBChannel): self._b = max(0.0, min(1.0,v) )
    
    def toNeoPixelRGBInt( self ) -> NeoPixelRGBInt:
        return (int(255*self._r) << 16) + (int(255*self._g) << 8) + (int(255*self._b)) # type: ignore
    
    def _set(self, r:RGBChannel, g:RGBChannel,b:RGBChannel):
        self.r = r
        self.g = g
        self.b = b
    
    def rgbTuple(self) -> RGBTuple:
        return (self.r, self.g, self.b)
        
    @staticmethod
    def fromNeoPixelRGBInt( npi:NeoPixelRGBInt ) ->RGB:
        #npi = int(npi)
        return RGB(
            r=((npi&0xFF0000)>>16)/255.0,
            g=((npi&0xFF00)>>8)/255.0,
            b=(npi&0xFF00)/255.0
        )
    
    def fadeTowards(self, other:RGB, ratio:ZeroToOne )->RGB:
        r2 = 1.0 - ratio
        return RGB(
            r = self.r * r2 + other.r * ratio,
            g = self.g * r2 + other.g * ratio,
            b = self.b * r2 + other.b * ratio,
        )

    @property
    def brightness(self)->float: 
        return (self.r + self.g + self.b) / 3.0
    
    def __repr__(self):
        return safeFmt( "(%.3f,%.3f,%.3f)", self.r, self.g, self.b)
    
    def __str__(self):
        return safeFmt( "(%.3f,%.3f,%.3f)", self.r, self.g, self.b)
    #Point = namedtuple('Point', ['x', 'y'])
        
    __colorRegex = re.compile( r"^#([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])$" )
    @staticmethod
    def lookupColor( color:str ):
        rv = getattr(RGB,color,None )
        if rv is None:
            m = RGB.__colorRegex.match( color )
            if m:
                hexColor = m.group(1)
                rv = RGB.fromNeoPixelRGBInt( int(hexColor, 16) ) # type: ignore
                return rv
            raise KeyError( safeFmt("unknown color %r",color) )
        if rv is None:
            return RGB.BLACK # type: ignore
        return rv

    @staticmethod
    def toRGB( value:AnyRGBValue )->RGB:

        #convertor = RGB.CONVERTORS.get(type(value).__name__,None)
        convertor = RGB.CONVERTORS.get(type(value),None)
        assert convertor is not None, safeFmt( "cannot convert %r (%s) to RGB", value, type(value))
        return convertor(value)
        
    #########################################################################
    CONVERTORS:dict[type, Callable[[Any],RGB]] = {
        float : lambda v: RGB( v, v, v ),
        bool : lambda v: RGB( 1,1,1 ) if v else RGB( 0, 0, 0 ),
        tuple : lambda v: RGB(v[0], v[1], v[2]),
        list : lambda v: RGB(v[0], v[1], v[2]),
    }

    BLACK:ClassVar[RGB]
    WHITE:ClassVar[RGB]
    
RGB.RED = RGB( "#FF0000" ) # type: ignore
RGB.BLUE = RGB( "#0000FF" ) # type: ignore
RGB.GREEN = RGB( "#00FF00" ) # type: ignore
RGB.BLACK = RGB( "#000000" ) # type: ignore
RGB.WHITE = RGB( "#FFFFFF" ) # type: ignore
RGB.YELLOW = RGB( "#FFFF00" ) # type: ignore
RGB.CYAN = RGB( "#00FFFF" ) # type: ignore

#############################################################################



AnyRGBValue:TypeAlias = Union[ RGB,
        int, float, bool,
        RGBTuple,
        # List [float],
        str, 
        
    ] 

#############################################################################

def registerToRGB( cf = lambda v:v):
    def r( cls:Type ):
        # print( f"registerToRGB {cls.__name__}")
        RGB.CONVERTORS[cls.__name__] = cf
        RGB.CONVERTORS[cls] = cf
        #RGB.CONVERTORS[cls.__name__] 
        return cls
    return r

#############################################################################
# RGB.CONVERTORS[RGB.__class__.__name__] = lambda v:v
RGB.CONVERTORS[RGB] = lambda v:v
RGB.CONVERTORS[int] = RGB.fromNeoPixelRGBInt
RGB.CONVERTORS[str] = RGB.lookupColor
