from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.Main.Expressions import OutputTarget, UpdateContext
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.util.bags import Bag

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


class RGB(object):
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
        return (int(255*self.__r) << 16) + (int(255*self.__g) << 8) + (int(255*self.__b))
    
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
    
class LightValueRGB(RGB, LightValueBase ):
    RED = RGB( 1, 0, 0 )
    BLUE = RGB( 0, 0, 1 )
    GREEN = RGB( 0, 1, 0 )
    BLACK = RGB( 0, 0, 0 )
    WHITE = RGB( 1, 1, 1 )
    
    CONVERTORS = {
        int: lambda v:RGB.fromNeoPixelInt(v),
        float: lambda v: RGB( v, v, v ),
        bool: lambda v: RGB( 1,1,1 ) if v else RGB( 0, 0, 0 ),
        tuple: lambda v: RGB(v[0], v[1], v[2]),
        list: lambda v: RGB(v[0], v[1], v[2]),
    }
    
    @staticmethod
    def toRGB( value:AnyLightValue )->RGB:
        
        convertor = LightValueRGB.CONVERTORS.get(type(value),None)
        if convertor is not None:
            return convertor(value)
        
        if isinstance( value, RGB):
            return value

        if isinstance( value, LightValueBase):
            return value.asRGB


        ensure( False, "cannot convert %r (%s) to RGB", value, type(value))

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

class LightValueNeoRGB(LightValueBase):
    __slots__ = "_LightValueNeoRGB__brightness", "_LightValueNeoRGB__value"

    CONVERTORS = {
        int: lambda v:v & 0xFFFFFF,
        float: lambda v: ( b255 := max(0,min(255,int(v * 255))), b255 + (b255 << 8) + (b255 << 16) )[1],
        bool: lambda v: 0xFFFFFF if v else 0,
        tuple: lambda v: (max(0,min(255,int(v[0]))) << 16) + (max(0,min(255,int(v[1]))) << 8) + (max(0,min(255,int(v[2])))),
        list: lambda v: (max(0,min(255,int(v[0]))) << 16) + (max(0,min(255,int(v[1]))) << 8) + (max(0,min(255,int(v[2])))),
    }
    @staticmethod
    def toNeoPixelInt( value:AnyLightValue )->int:
        convertor = LightValueNeoRGB.CONVERTORS.get(type(value),None)
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

class LightGroupBase(NamedLocalIdentifiable):
    """ a group of related lights used for a common purpose

    Args:
        object (_type_): _description_
    """
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    @property
    def lightCount(self) -> int: raise NotImplemented
        
    @property
    def lights(self) -> Iterable["LightBase"] : raise NotImplemented
    
    def __getitem__(self, index:int) -> "LightBase": raise NotImplemented

    def __setitem__(self, index:int, value:AnyLightValue ): 
        self[index].setValue(value)
    
    def values(self,  context: UpdateContext = None ):
        return [ light.getValue(context) for light in self.lights]
                
#############################################################################

class LightGroupListBase(LightGroupBase):
    def __init__(self, lights:List["LightBase"] = [], name:str|None=None,**kwargs):
        super().__init__(name=name,**kwargs)
        self.__lights:List["LightBase"] = lights

    @property
    def lightCount(self) -> int: return len(self.__lights)
    
    @property
    def lights(self) -> Iterable["LightBase"] :
        return iter(self.__lights)
    
    def __getitem__(self, index) -> "LightBase":
        return self.__lights[index]

    def __setitem__(self, index, value:AnyLightValue ):
        self.__lights[index].setValue(value)

#############################################################################

class NextNLights(LightGroupListBase):
    def __init__(self,count:int,name:str, source:"LightSourceBase",**kwargs):
        
        offset = source.startOfNextN(count)
        lights = list( [source[offset + index] for index in range(count)] )
        super().__init__(name=name,lights=lights,**kwargs)

#############################################################################

class AdHocLightGroup(LightGroupListBase):
    def __init__(self,name:str,**kwargs):
        self.__adHocLights = []
        super().__init__(name=name,lights=self.__adHocLights,**kwargs)
        
    def append(self, light:"LightBase"|LightGroupBase):
        if isinstance(light, LightGroupBase):
            for l2 in LightGroupBase.lights:
                self.append(l2)
            return
        ensure( light not in self.__adHocLights, "light %s already in %s", light, self )
        self.__adHocLights.append( light )

#############################################################################

class LightSourceBase(LightGroupListBase):
    """ driver / hardware interface providing Lights"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__nextGroupStartIndex = 0

    def startOfNextN(self, count:int ):
        rv = self.__nextGroupStartIndex 
        ensure( self.__nextGroupStartIndex + count  <= self.lightCount, "not enough lights remaining" )
        self.__nextGroupStartIndex += count
        return rv
    
    def nextNLights(self, count:int, name:str=None, **kwargs ) ->NextNLights:
        return NextNLights( count=count,
                           name=name or f"{self.name}[{self.__nextGroupStartIndex}:{self.__nextGroupStartIndex+count-1}]", 
                           source=self,**kwargs )
    
    def lightChanged(self,light:"LightBase"): raise NotImplemented
    

class LightType:
    LT_SINGLE_SOLID=1
    LT_SINGLE_DIMMABLE=3
    LT_RGB=4
    
    #LT_TYPES = Required[ LT_SINGLE_SOLID | LT_SINGLE_DIMMABLE | LT_RGB ]
    
#############################################################################
class LightBase(OutputTarget):
    
    def __init__(self, source:LightSourceBase=None, index:int = 0, name:str|None = None):
        super().__init__(name=name)
        assert source is not None
        self.__source:LightSourceBase = source
        self.__sourceIndex:int = index
        
    @property
    def source(self)->LightSourceBase: return self.__source
    
    @property
    def sourceIndex(self)->int: return self.__sourceIndex
    
    def setValue(self,value:AnyLightValue, context: UpdateContext = None ):
        raise NotImplemented

    @property
    def value(self): return self.getValue()
    
    def getValue(self, context: UpdateContext = None ) -> AnyLightValue:
        raise NotImplemented
    
    def getLightValue(self)-> LightValueBase: raise NotImplemented  
    
    def getRGB(self):
        return self.getLightValue().asRGB
    
    @property
    def lightType(self): raise NotImplemented  

class SingleColorLightBase(LightBase):
    """ for regular single color LEDs"""
    
    @property
    def lightType(self): return LightType.LT_SINGLE_SOLID

class SingleColorDimmableLightBase(LightBase):
    """ for regular single color LEDs"""
    
    @property
    def lightType(self): return LightType.LT_SINGLE_DIMMABLE
    
class RGBLightBase(LightBase):
    @property
    def lightType(self): return LightType.LT_RGB


#############################################################################
