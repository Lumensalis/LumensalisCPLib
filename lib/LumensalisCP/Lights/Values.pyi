from LumensalisCP.IOContext import *

import rainbowio
from random import random as randomZeroToOne, randint

def wheel255( val:float ): return rainbowio.colorwheel(val)

def wheel1( val:float ): return rainbowio.colorwheel(val*255.0)



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

if LCPF_TYPING_IMPORTED:
    

    type AnyLightValue = Union[
         int, float, bool,
         Tuple[float,float,float],
         List [float],
        str
     ] 
else:
    AnyLightValue = None

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
    
    def setLight(self, value|AnyLightValue): pass

    @property
    def asNeoPixelInt(self)->int: pass
    
    @property
    def asRGB(self) -> RGB: pass


#############################################################################
"""
another possible hack - not sure this would work and it's moderately ugly but....   
before your **_make_board_completion** you could add
```
source <LOCATION_OF_BASH_COMPLITION_BUILTINS>/make
```
which should pull in the "default" implementation as **_comp_cmd_make**, 
and then insert 
```
        else 
            _comp_cmd_make
```
at the end of **_make_board_completion**  (before `fi`) - that might make it
fall through to the original behavior when yours doesn't match?

"""