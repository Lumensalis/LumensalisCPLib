from LumensalisCP.Main.Updates import Evaluatable
from LumensalisCP.common import *

import rainbowio
from random import random as randomZeroToOne, randint

def wheel255( val:float ): return rainbowio.colorwheel(val)

def wheel1( val:float ): return rainbowio.colorwheel(val*255.0)



from collections import namedtuple
AnyLightValue = Union[
        int, float, bool,
        Tuple[float,float,float],
        List [float],
    str
    ] 

class RGB(object):
    # __slots__ = [ '_r', '_g', '_b' ]
    
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
    def __init__(self, r:ZeroToOne|tuple|"RGB"=0, g:Optional[ZeroToOne]=None, b:Optional[ZeroToOne]=None ):
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
        return (int(255*self._r) << 16) + (int(255*self._g) << 8) + (int(255*self._b))
    
    def _set(self, r:ZeroToOne, g:ZeroToOne,b:ZeroToOne):
        self.r = r
        self.g = g
        self.b = b
    
    def _rgbTuple(self) -> Tuple[ZeroToOne,ZeroToOne,ZeroToOne]:
        return (self.r, self.g, self.b)
        
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
        return safeFmt( "(%.3f,%.3f,%.3f)", self.r, self.g, self.b)
    
    def __str__(self):
        return safeFmt( "(%.3f,%.3f,%.3f)", self.r, self.g, self.b)
    #Point = namedtuple('Point', ['x', 'y'])
    
    
# RGB.CONVERTORS[RGB.__class__.__name__] = lambda v:v
RGB.CONVERTORS['RGB'] = lambda v:v



class LightValueBase(object):
    def __init__(self, *args, **kwds):
        pass

    @property
    def brightness(self)->float: raise NotImplementedError

    @property
    def asNeoPixelInt(self)->int: raise NotImplementedError
    
    @property
    def asRGB(self) -> RGB: raise NotImplementedError

    def setLight(self, value) ->None: raise NotImplementedError

def registerToRGB( cf = lambda v:v):
    def r( cls ):
        # print( f"registerToRGB {cls.__name__}")
        RGB.CONVERTORS[cls.__name__] = cf
        #RGB.CONVERTORS[cls.__name__] 
        return cls
    return r

@registerToRGB( lambda v: v )
class LightValueRGB(RGB, LightValueBase ):
    RED = RGB( 1, 0, 0 )
    YELLOW = RGB( 1, 1, 0 )
    BLUE = RGB( 0, 0, 1 )
    GREEN = RGB( 0, 1, 0 )
    BLACK = RGB( 0, 0, 0 )
    WHITE = RGB( 1, 1, 1 )
    
    @staticmethod
    def lookupColor( color:str ):
        rv = getattr(LightValueRGB,color,None )
        if rv is None:
            raise KeyError( safeFmt("unknown color %r",color) )
        if rv is None:
            return LightValueRGB.BLACK
        return rv

    @staticmethod
    def toRGB( value:AnyLightValue )->RGB:
        
        convertor = RGB.CONVERTORS.get(type(value).__name__,None)
        assert convertor is not None, safeFmt( "cannot convert %r (%s) to RGB", value, type(value))
        return convertor(value)
        
    @staticmethod
    def prepRGBValue( value ):
        if (
                isinstance( value, Evaluatable ) or
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
        
        assert False,  safeFmt("cannot convert %r (%s) to NeoRGB", value, type(value))
    
    
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
