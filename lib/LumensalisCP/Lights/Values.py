from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.Main.Expressions import OutputTarget, UpdateContext
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.util.bags import Bag
import LumensalisCP.Main.Expressions as xm

import rainbowio
from random import random as randomZeroToOne, randint

def wheel255( val:float ): return rainbowio.colorwheel(val)

def wheel1( val:float ): return rainbowio.colorwheel(val*255.0)

AnyLightValue = Any

class LightValueBase(object):
    def __init__(self, *args, **kwds):
        pass

    @property
    def brightness(self)->float: raise NotImplemented

    @property
    def asNeoPixelInt(self)->int: raise NotImplemented
    
    @property
    def asRGB(self) -> "RGB": raise NotImplemented

    def setLight(self, value): raise NotImplemented


from collections import namedtuple

class RGB(object):
    __slots__ = [ '_r', '_g', '_b' ]
    
    CONVERTORS = dict(
        int= lambda v:RGB.fromNeoPixelInt(v),
        float= lambda v: RGB( v, v, v ),
        bool= lambda v: RGB( 1,1,1 ) if v else RGB( 0, 0, 0 ),
        tuple= lambda v: RGB(v[0], v[1], v[2]),
        list= lambda v: RGB(v[0], v[1], v[2]),
        str= lambda v: LightValueRGB.lookupColor(v),
        #**dict([
        #    [RGB.__class__.__name__, lambda v:v ]
        #])
    )
    def __init__(self, r:ZeroToOne|tuple|"RGB"=0, g:ZeroToOne|None=None, b:ZeroToOne|None=None ):
        super().__init__()
        if g is None:
            ensure( type(b) is None, "b must also be None" )
            if r is None:
                r,g,b = 0.0,0.0,0.0
            elif type(r) is tuple:
                r, b, g = r
            elif isinstance(r,RGB):
                r, b, g = r.r, r.b, r.g
                
        #r = withinZeroToOne( r ) 
        #g = withinZeroToOne( g ) 
        #b = withinZeroToOne( b ) 

        #self.extend( (r,g,b) )
        self._r =  withinZeroToOne( r )
        self._g =  withinZeroToOne( g )
        self._b =  withinZeroToOne( b )
        #ensure( len(self) == 3 )
        
    @property 
    def r(self)->ZeroToOne: return self._r
    @r.setter
    def r(self,v): self._r = max(0.0, min(1.0,v) )
    
    @property 
    def g(self)->ZeroToOne: return self._g
    @g.setter
    def g(self,v): self._g = max(0.0, min(1.0,v) )
    
    @property 
    def b(self)->ZeroToOne: return self._b
    @b.setter
    def b(self,v): self._b = max(0.0, min(1.0,v) )
    
    def toNeoPixelInt( self ):
        return (int(255*self._r) << 16) + (int(255*self._b) << 8) + (int(255*self._g))
    
    def _set(self, r:ZeroToOne, g:ZeroToOne,b:ZeroToOne):
        self.r = r
        self.g = g
        self.b = b
    
    def _rgbTuple(self) -> Tuple[ZeroToOne,ZeroToOne,ZeroToOne]:
        return self
        
    @staticmethod
    def fromNeoPixelInt( npi:int ) ->"RGB":
        npi = int(npi)
        return RGB(
            r=((npi&0xFF0000)>>16)/255.0,
            g=((npi&0xFF00)>>8)/255.0,
            b=(npi&0xFF00)/255.0
        )
    
    def fadeTowards(self, other:"RGB", ratio:ZeroToOne )->"RGB":
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
        return safeFmt( "(%r,%r,%r)", self.r, self.g, self.b)
    
    def __str__(self):
        return safeFmt( "(%r,%r,%r)", self.r, self.g, self.b)
    #Point = namedtuple('Point', ['x', 'y'])
    
    
RGB.CONVERTORS[RGB.__class__.__name__] = lambda v:v
RGB.CONVERTORS['RGB'] = lambda v:v

if 0:
     """
    class RGBNT(namedtuple('RGBBase', ['_r', '_g','_b'])):
        #__slots__ = '_RGB__r', '_RGB__g', '_RGB__b'

        def __init__(self, r:ZeroToOne=0, b:ZeroToOne=0, g:ZeroToOne=0 ):
            super().__init__(r,g,b)
            if type(r) is float:
                self.r:ZeroToOne = r
                self.g:ZeroToOne = g
                self.b:ZeroToOne = b
            else:
                if type(r) is tuple:
                    r, b, g = r
                if isinstance(r,RGB):
                    r, b, g = r.r, r.b, r.g
                    
                self.r:ZeroToOne = r
                self.g:ZeroToOne = g
                self.b:ZeroToOne = b
        
        @property 
        def r(self)->ZeroToOne: return self._r
        @r.setter
        def r(self,v): self._r = max(0.0, min(1.0,v) )
        
        @property 
        def g(self)->ZeroToOne: return self._b
        @g.setter
        def g(self,v): self._g = max(0.0, min(1.0,v) )
        
        @property 
        def b(self)->ZeroToOne: return self._g
        @b.setter
        def b(self,v): self._b = max(0.0, min(1.0,v) )
        
        def toNeoPixelInt( self ):
            return (int(255*self.r) << 16) + (int(255*self.b) << 8) + (int(255*self.g))
        
        def _set(self, r:ZeroToOne, g:ZeroToOne,b:ZeroToOne):
            self.r = r
            self.g = g
            self.b = b
        
        def _rgbTuple(self) -> Tuple[ZeroToOne,ZeroToOne,ZeroToOne]:
            return self
            
        @staticmethod
        def fromNeoPixelInt( npi:int ) ->"RGB":
            npi = int(npi)
            return RGB(
                r=((npi&0xFF0000)>>16)/255.0,
                g=((npi&0xFF00)>>8)/255.0,
                b=(npi&0xFF00)/255.0
            )
        
        def fadeTowards(self, other:"RGB", ratio:ZeroToOne )->"RGB":
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
            return safeFmt( "(%r,%r,%r)", self.r, self.g, self.b)
        
    class RGBD(object):
        __slots__ = '_RGB__r', '_RGB__g', '_RGB__b'

        def __init__(self, r:ZeroToOne=0, b:ZeroToOne=0, g:ZeroToOne=0 ):
            if type(r) is float:
                self.r:ZeroToOne = r
                self.g:ZeroToOne = g
                self.b:ZeroToOne = b
            else:
                if type(r) is tuple:
                    r, b, g = r
                if isinstance(r,RGB):
                    r, b, g = r.r, r.b, r.g
                    
                self.r:ZeroToOne = r
                self.g:ZeroToOne = g
                self.b:ZeroToOne = b
        
        @property 
        def r(self)->ZeroToOne: return self.__r
        @r.setter
        def r(self,v): self.__r = max(0.0, min(1.0,v) )
        
        @property 
        def g(self)->ZeroToOne: return self.__g
        @g.setter
        def g(self,v): self.__g = max(0.0, min(1.0,v) )
        
        @property 
        def b(self)->ZeroToOne: return self.__b
        @b.setter
        def b(self,v): self.__b = max(0.0, min(1.0,v) )
        
        def toNeoPixelInt( self ):
            return (int(255*self.__r) << 16) + (int(255*self.__b) << 8) + (int(255*self.__g))
        
        def _set(self, r:ZeroToOne, g:ZeroToOne,b:ZeroToOne):
            self.__r = r
            self.__g = g
            self.__b = b
        
        def _rgbTuple(self) -> Tuple[ZeroToOne,ZeroToOne,ZeroToOne]:
            return (self.__r,self.__g,self.__b)
            
        @staticmethod
        def fromNeoPixelInt( npi:int ) ->"RGB":
            npi = int(npi)
            return RGB(
                r=((npi&0xFF0000)>>16)/255.0,
                g=((npi&0xFF00)>>8)/255.0,
                b=(npi&0xFF00)/255.0
            )
        
        def fadeTowards(self, other:"RGB", ratio:ZeroToOne )->"RGB":
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
            return safeFmt( "(%r,%r,%r)", self.r, self.g, self.b)
        
"""   

def registerToRGB( cf = lambda v:v):
    def r( cls ):
        print( f"registerToRGB {cls.__name__}")
        RGB.CONVERTORS[cls.__name__] = cf
        #RGB.CONVERTORS[cls.__name__] 
        return cls
    return r

@registerToRGB( lambda v: v )
class LightValueRGB(RGB, LightValueBase ):
    RED = RGB( 1, 0, 0 )
    BLUE = RGB( 0, 0, 1 )
    GREEN = RGB( 0, 1, 0 )
    BLACK = RGB( 0, 0, 0 )
    WHITE = RGB( 1, 1, 1 )
    
    @staticmethod
    def lookupColor( color:str ):
        rv = getattr(LightValueRGB,color,None )
        if rv is None:
            raise KeyError( safeFmt("unknown color %r",color) )
        
        return rv

    @staticmethod
    def toRGB( value:AnyLightValue )->RGB:
        
        convertor = RGB.CONVERTORS.get(type(value).__name__,None)
        if convertor is not None:
            return convertor(value)
        
        #if isinstance( value, RGB):
        #    return value

        # if isinstance( value, LightValueBase): return value.asRGB

        ensure( False, "cannot convert %r (%s) to RGB", value, type(value))

    @staticmethod
    def prepRGBValue( value ):
        if (
                isinstance( value, xm.ExpressionTerm ) or
                isinstance( value, xm.Expression ) or
                callable(value)
        ):
            return value
        
        return LightValueRGB.toRGB( value )
        
    def setLight(self, value):
        v = LightValueRGB.toRGB( value )
        self._set( *v._rgbTuple() )

    @staticmethod
    def randomRGB( brightness:ZeroToOne=1) -> RGB:
        return RGB( randomZeroToOne() * brightness,  randomZeroToOne() * brightness,  randomZeroToOne() * brightness )

    @property
    def asNeoPixelInt(self)->int: 
        return self.toNeoPixelInt()
    
    @property
    def asRGB(self) -> RGB:
        return RGB( self._rgbTuple() )

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
    def toNeoPixelInt( value:AnyLightValue )->int:
        convertor = LightValueNeoRGB.NP_INT_CONVERTORS.get(type(value).__name__,None)
        if convertor is not None:
            return convertor(value)

        if isinstance( value, LightValueBase):
            return value.asNeoPixelInt
        elif isinstance( value, RGB ):
            return value.toNeoPixelInt()
        
        ensure( False, "cannot convert %r (%s) to NeoRGB", value, type(value))
    
    
    @staticmethod
    def formatNeoRGBValues( values ):
        return '|'.join( [('%6.6X'%LightValueNeoRGB.toNeoPixelInt(v)) for v in values])
    
    def __init__(self,  value:AnyLightValue ):
        self.__value = LightValueNeoRGB.toNeoPixelInt( value )
        self.__brightness = 1.0

    @staticmethod
    def randomRGB( brightness:ZeroToOne=1):
        def rChannel(): return randint(0,int(255*brightness))
        return (rChannel() << 16) + (rChannel() << 8) +  rChannel()

    @property
    def brightness(self)->float: return self.__brightness
    
    def setLight(self, value):
        self.__value = LightValueNeoRGB.toNeoPixelInt( value )

    @property
    def asNeoPixelInt(self)->int: return self.__value
    
    @property
    def asRGB(self) -> RGB:
        return RGB.fromNeoPixelInt( self.__value )



#############################################################################
