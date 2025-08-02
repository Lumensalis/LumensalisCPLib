from __future__ import annotations

#############################################################################

from random import random as randomZeroToOne, randint # pyright: ignore[reportUnusedImport]
import re

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayLightsRGBImport = getImportProfiler( globals() ) # "Lights.RGB"

#from LumensalisCP.CPTyping import TypeAlias, ZeroToOne,Union, Type, Callable, Optional,  Any, Tuple, NewType, ClassVar
#from LumensalisCP.CPTyping import Generic, TypeVar
from LumensalisCP.CPTyping import *

from LumensalisCP.common import withinZeroToOne_, safeFmt, ZeroToOne
from LumensalisCP.util.Convertor import Convertor
#from LumensalisCP.Eval.Evaluatable import Evaluatable, evaluate

#from LumensalisCP.CPTyping import *

_sayLightsRGBImport.parsing()

RGBChannel:TypeAlias = ZeroToOne

RGBTuple:TypeAlias = Tuple[RGBChannel,RGBChannel,RGBChannel]


#############################################################################
NeoPixelRGBInt = NewType('NeoPixelRGBInt', int)

AnyRGBValue:TypeAlias = Union[ 'RGB',
        int, float, bool,
        RGBTuple,
        # List [float],
        str, 
    ] 


class RGB(object):
    

    def __init__(self, r:RGBChannel|tuple[float,float,float]|str|RGB=0.0, g:Optional[RGBChannel]=None, b:Optional[RGBChannel]=None ) -> None:
        
        super().__init__()
        #self.__rgb:int = 0
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
        
        self.__rgb:int = (
                (int(withinZeroToOne_( r )*255) << 16) +
                (int(withinZeroToOne_( g )*255) << 8) + 
                int(withinZeroToOne_( b )*255)
        )

    if True:
        @property 
        def r(self)->RGBChannel: return (self.__rgb>>16 & 0xFF)/255.0
        @r.setter
        def r(self,v:RGBChannel) -> None: 
            v = int(max(0.0, min(1.0,v)) * 255)
            self.__rgb = (self.__rgb & 0x00FFFF) | (v << 16)

        @property 
        def g(self)->RGBChannel: return (self.__rgb>>8 & 0xFF)/255.0
        @g.setter
        def g(self,v:RGBChannel) -> None: 
            v = int(max(0.0, min(1.0,v)) * 255)
            self.__rgb = (self.__rgb & 0xFF00FF) | (v << 8)
        
        @property 
        def b(self)->RGBChannel: return (self.__rgb & 0xFF)/255.0
        @b.setter
        def b(self,v:RGBChannel) -> None: 
            v = int(max(0.0, min(1.0,v)) * 255)
            self.__rgb = (self.__rgb & 0xFFFF00) | v
        
        def asNeoPixelRGBInt( self ) -> NeoPixelRGBInt:
            return self.__rgb # type: ignore
        
        def __hash__(self) -> int:
            return self.__rgb
        def __eq__(self, value: object) -> bool:
            if isinstance(value, RGB):
                return self.__rgb == value.__rgb
            return False
    else:
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
        
        def asNeoPixelRGBInt( self ) -> NeoPixelRGBInt:
            return (int(255*self.r) << 16) + (int(255*self.g) << 8) + (int(255*self.b)) # type: ignore


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
            b=(npi&0xFF)/255.0
        )
    
    def setFromNeoPixelRGBInt( self, npi:NeoPixelRGBInt ) -> None:
        self.r=((npi&0xFF0000)>>16)/255.0
        self.g=((npi&0xFF00)>>8)/255.0
        self.b=(npi&0xFF)/255.0
        
    
    def fadeTowards(self, other:RGB, ratio:ZeroToOne )->RGB:
        r2 = 1.0 - ratio
        return RGB(
            r = self.r * r2 + other.r * ratio,
            g = self.g * r2 + other.g * ratio,
            b = self.b * r2 + other.b * ratio,
        )

    def fadeAB(self, a:RGB, b:RGB, ratio:ZeroToOne )->None:
        r2 = 1.0 - ratio
        self.r = a.r * r2 + b.r * ratio
        self.g = a.g * r2 + b.g * ratio
        self.b = a.b * r2 + b.b * ratio
        
    
    @property
    def brightness(self)->float: 
        return (self.r + self.g + self.b) / 3.0
    
    def __repr__(self):
        return safeFmt( "(%.3f,%.3f,%.3f)", self.r, self.g, self.b)
        #    return safeFmt( "(%.3f,%.3f,%.3f)", self.r, self.g, self.b)

    def __str__(self):
        return safeFmt( "(%.3f,%.3f,%.3f)", self.r, self.g, self.b)
    #Point = namedtuple('Point', ['x', 'y'])
        
    __colorRegex = re.compile( r"^#([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])$" )
    __hexVal = { '0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7,
                 '8':8, '9':9, 'A':10, 'B':11, 'C':12, 'D':13, 'E':14, 'F':15,
                 'a':10, 'b':11, 'c':12, 'd':13, 'e':14, 'f':15 }
    
    @staticmethod
    def lookupColor( color:str ):
        #try:
        #    return getattr(Colors,color)
        #except (NameError,AttributeError): pass
        if True:

            if color.startswith("#") and len(color) == 7:
                if True:
                    hexInt = int(color[1:], 16)
                    return RGB.fromNeoPixelRGBInt( hexInt ) # type: ignore

                    r = (hexInt >> 16) & 0xFF
                    g = (hexInt >> 8) & 0xFF
                    b = hexInt & 0xFF
                else:
                    r = RGB.__hexVal[color[1]]*16 + RGB.__hexVal[color[2]]
                    g = RGB.__hexVal[color[3]]*16 + RGB.__hexVal[color[4]]
                    b = RGB.__hexVal[color[5]]*16 + RGB.__hexVal[color[6]]

                return RGB(r/255.0,g/255.0,b/255.0)
        else:
            m = RGB.__colorRegex.match( color )
            if m:
                hexColor = m.group(1)
                rv = RGB.fromNeoPixelRGBInt( int(hexColor, 16) ) # type: ignore
                return rv

            
        rv = getattr(Colors,color,None)
        if rv is not None:
            return rv 

        raise KeyError( safeFmt("unknown color %r",color) )
        
    @staticmethod
    def toRGB( value:AnyRGBValue )->RGB:

        #convertor = Colors.Convertors.get(type(value).__name__,None)
        return RGB.Convertors(value)
        
    #########################################################################
    Convertors:ClassVar[Convertor[AnyRGBValue,RGB]] 
    Convertors = Convertor()

class Colors:
    BLACK = RGB("#000000")
    WHITE = RGB("#FFFFFF")
    RED = RGB("#FF0000")
    BLUE = RGB("#0000FF")
    GREEN = RGB("#00FF00")
    YELLOW = RGB("#FFFF00")
    CYAN = RGB("#00FFFF")
    MAGENTA = RGB("#FF00FF")
    ORANGE = RGB("#FFA500")
    PURPLE = RGB("#800080")
    PINK = RGB("#FFC0CB")
    GRAY = RGB("#808080")
    LIGHT_GRAY = RGB("#D3D3D3")
    DARK_GRAY = RGB("#A9A9A9")
    LIGHT_BLUE = RGB("#ADD8E6")
    LIGHT_GREEN = RGB("#90EE90")


#############################################################################
# Colors.Convertors[RGB.__class__.__name__] = lambda v:v
@RGB.Convertors.defineRegisterConvertor( float ) 
def floatToRGB( v:float ) -> RGB: return RGB( v, v, v )

@RGB.Convertors.defineRegisterConvertor( bool )
def boolToRGB( v:bool ) -> RGB: return RGB( 1,1,1 ) if v else RGB( 0, 0, 0 )

@RGB.Convertors.defineRegisterConvertor( tuple )
def tupleToRGB( v:tuple[float,float,float] ) -> RGB: return RGB( v[0], v[1], v[2] )

@RGB.Convertors.defineRegisterConvertor( list )
def listToRGB( v:list[float] ) -> RGB: return RGB( v[0], v[1], v[2] )

@RGB.Convertors.defineRegisterConvertor( RGB )
def rgbToRGB( v:RGB ) -> RGB: return v

@RGB.Convertors.defineRegisterConvertor( int )
def intToRGB( v:int ) -> RGB: return RGB.fromNeoPixelRGBInt( v ) # pyright: ignore[reportArgumentType]

@RGB.Convertors.defineRegisterConvertor( str )
def strToRGB( v:str ) -> RGB: return RGB.lookupColor( v )

_sayLightsRGBImport.complete(globals())

__all__ = [
    'RGB', 'Colors', 'RGBChannel', 'RGBTuple', 'NeoPixelRGBInt', 'AnyRGBValue',
]
