# SPDX-FileCopyrightText: 2025 James Fowler
#
"""
`LumensalisCP.Lights.RGB`
====================================================
provides RGB color class and related utilities
"""

# #############################################################################
from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler
__profileImport = getImportProfiler( __name__, globals() ) 
#############################################################################

from LumensalisCP.CPTyping import *
from LumensalisCP.common import withinZeroToOne_, safeFmt, ZeroToOne
from LumensalisCP.util.Convertor import Convertor
from LumensalisCP.util.Setter import Setter
from LumensalisCP.util.CountedInstance import CountedInstance

#############################################################################

__profileImport.parsing()

# type aliases
RGBChannel:TypeAlias = ZeroToOne
RGBTuple:TypeAlias = Tuple[RGBChannel,RGBChannel,RGBChannel]
NeoPixelRGBInt = NewType('NeoPixelRGBInt', int)
AnyRGBValue:TypeAlias = Union[ 'RGB',
        int, float, bool,
        RGBTuple,
        # List [float],
        str, 
        NeoPixelRGBInt,
    ] 

#############################################################################
class RGBInterface(Protocol):

    def __init__(self, 
                 r:Optional[RGBChannel|tuple[float,float,float]|str|RGB]=None, 
                 g:Optional[RGBChannel]=None, 
                 b:Optional[RGBChannel]=None 
    ) -> None: ...

    @property 
    def r(self)->RGBChannel: ...
    @r.setter
    def r(self,v:RGBChannel) -> None:  ...
            
    @property 
    def g(self)->RGBChannel: ...
    @g.setter
    def g(self,v:RGBChannel) -> None:  ...

    @property 
    def b(self)->RGBChannel: ...
    @b.setter
    def b(self,v:RGBChannel) -> None: ...

    @property
    def brightness(self)->float: ...

    def asNeoPixelRGBInt( self ) -> NeoPixelRGBInt: ...
    def rgbTuple(self) -> RGBTuple: ...
    def fadeTowards(self, other:RGB, ratio:ZeroToOne )->RGB: ...

    # MODIFY IN PLACE methods
    def setFromNeoPixelRGBInt( self, npi:NeoPixelRGBInt ) -> None: ...
    def setToColorString( self, color:str ) -> None: ...
    def fadeAB(self, a:RGB, b:RGB, ratio:ZeroToOne )->None: ...
    

    @staticmethod
    def lookupColor( color:str )-> RGB|None: ...
    @staticmethod
    def toRGB( value:AnyRGBValue )->RGB: ...
    @staticmethod
    def fromNeoPixelRGBInt( npi:NeoPixelRGBInt ) ->RGB: ...
    
    def _set_r_g_b(self, r:RGBChannel, g:RGBChannel,b:RGBChannel) -> None: ...
    def _set_Any(self, v:AnyRGBValue) -> None: ...
    def _set_RGB(self, v:RGBInterface) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __hash__(self) -> int: ...
    def __eq__(self, value: object) -> bool: ...


#############################################################################
__RGB_STORE_AS_INT = True
# pyright: reportRedeclaration=false
class RGB(CountedInstance,RGBInterface):
    """ RGB color with 0.0 to 1.0 float values for each channel (r/g/b)"""

    def __init__(self, 
                 r:Optional[RGBChannel|tuple[float,float,float]|str|RGB]=None, 
                 g:Optional[RGBChannel]=None, 
                 b:Optional[RGBChannel]=None 
    ) -> None:
        CountedInstance.__init__(self)

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
                raise TypeError(f"Invalid type ({type(r)}):{r} for RGB initialization") 
        
        self._set_r_g_b(r,g,b) # type: ignore

    def rgbTuple(self) -> RGBTuple:
        return (self.r, self.g, self.b)
    
    def _set_Any(self, v:AnyRGBValue) -> None: 
        if isinstance(v, RGB):
            self._set_RGB(v)
        elif isinstance(v, int ): #(int,NeoPixelRGBInt)):
            self.setFromNeoPixelRGBInt(v) # type: ignore
        elif isinstance(v, str):
            self.setToColorString(v)
        elif isinstance(v, (list, tuple)):
            assert len(v) == 3, "List or tuple must have exactly 3 elements for RGB"
            self._set_r_g_b( v[0], v[1], v[2] )
        else:
            other = RGB.toRGB(v)
            self._set_RGB(other)
            
    def _set_RGB(self, v:RGBInterface) -> None: 
        self._set_r_g_b( v.r, v.g, v.b ) 
    
    @staticmethod
    def fromNeoPixelRGBInt( npi:NeoPixelRGBInt ) ->RGB:
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
 
    def __str__(self):
        return safeFmt( "(%.3f,%.3f,%.3f)", self.r, self.g, self.b)
        
    # __colorRegex = __regex.compile( r"^#([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])$" )
    __hexVal = { '0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7,
                 '8':8, '9':9, 'A':10, 'B':11, 'C':12, 'D':13, 'E':14, 'F':15,
                 'a':10, 'b':11, 'c':12, 'd':13, 'e':14, 'f':15 }
    
    @staticmethod
    def lookupColor( color:str ):
        rv = RGB()
        rv.setToColorString(color)
        return rv
    
    def setToColorString( self, color:str ) -> None:

        if color.startswith("#") and len(color) == 7:
            # these are easier - but trigger allocations
            # hexInt = int(color[1:], 16)
            # match = RGB.__colorRegex.match(color)
            hexInt = 0
            for i in range(1,7):
                cv = RGB.__hexVal.get(color[i], None)
                assert cv is not None, safeFmt("Invalid hex digit %r", color[i])
                hexInt = (hexInt << 4) | cv
            self.setFromNeoPixelRGBInt( hexInt ) # type: ignore
        else:
            rv = getattr(Colors,color,None)
            if rv is None:
                raise KeyError( safeFmt("unknown color %r",color) )
            self._set_RGB(rv)
        
    def setFrom( self, value:AnyRGBValue) -> None:
        RGB.Setters(value, self)

    @staticmethod
    def toRGB( value:AnyRGBValue )->RGB:
        return RGB.Convertors(value)
    
    @staticmethod
    def toRGB( value:AnyRGBValue )->RGB:
        return RGB.Convertors(value)
        
    #########################################################################
    Convertors:ClassVar[Convertor[AnyRGBValue,RGB]] 
    Convertors = Convertor()

    Setters:ClassVar[Setter[AnyRGBValue,RGB]]   
    Setters = Setter() 

    #########################################################################
    # define r/g/b properties - using RGBChannel but internally storing as 
    # either three RGBChannels or a single int
    
    if __RGB_STORE_AS_INT:
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
        
        def _set_r_g_b(self, r:RGBChannel, g:RGBChannel,b:RGBChannel) -> None:
            self.__rgb:int = (
                    (int(withinZeroToOne_( r )*255) << 16) +
                    (int(withinZeroToOne_( g )*255) << 8) + 
                    int(withinZeroToOne_( b )*255)
            )
        
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

        def _set_r_g_b(self, r:RGBChannel, g:RGBChannel,b:RGBChannel) -> None:
            self.r = r
            self.g = g
            self.b = b


#############################################################################

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

# pyright: reportRedeclaration=false, reportPrivateUsage=false
#############################################################################

@RGB.Setters.defineRegisterSetter( tuple )
def _( v:tuple[float,float,float], target:RGB ) -> None:
    assert len(v) == 3
    target._set_r_g_b( v[0], v[1], v[2] )

@RGB.Setters.defineRegisterSetter( list )
def _( v:list[float], target:RGB ) -> None:
    assert len(v) == 3
    target._set_r_g_b( v[0], v[1], v[2] )

@RGB.Setters.defineRegisterSetter( RGB )
def _( v:RGB, target:RGB ) -> None:
    target._set_RGB(v)

@RGB.Setters.defineRegisterSetter( int )
def _( v:int, target:RGB ) -> None:
    target.setFromNeoPixelRGBInt(int)

@RGB.Setters.defineRegisterSetter( str )
def _( v:str, target:RGB ) -> None:
    target.setToColorString(v)


__all__ = [
    'RGB', 'Colors', 'RGBChannel', 'RGBTuple', 'NeoPixelRGBInt', 'AnyRGBValue',
]

__profileImport.complete()