from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.Main.Expressions import InputSource, Expression, ExpressionTerm, UpdateContext
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
import rainbowio

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
    def asRGB(self) -> Mapping: raise NotImplemented

    def setLight(self, value): raise NotImplemented


class LightValueNeoRGB(object):
    @staticmethod
    def toNeoPixelInt( value:AnyLightValue )->int:
        if type(value) is int:
            return value
        if isinstance( value, LightValueBase):
            return value.asNeoPixelInt
        if type(value) is float:
            b255 = max(0,min(255,int(value * 255)))
            return b255 + (b255 << 8) + (b255 << 16)
        if type is True:
            return 0xFFFFFF
        if type is False:
            return 0
        raise NotImplemented
    
    def __init__(self,  value:AnyLightValue ):
        self.__value = LightValueNeoRGB.toNeoPixelInt( value )
        self.__brightness = 1.0

    @property
    def brightness(self)->float: return self.__brightness
    
    def setLight(self, value):
        self.__value = LightValueNeoRGB.toNeoPixelInt( value )

    @property
    def asNeoPixelInt(self)->int: return self.__value
    
    @property
    def asRGB(self) -> Mapping: raise NotImplemented


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
    
    def __getitem__(self, index) -> "LightBase": raise NotImplemented

    def __setitem__(self, index, value:AnyLightValue ): 
        self[index].setValue(value)
        
#############################################################################

class LightGroupListBase(LightGroupBase):
    def __init__(self,name:str, lights:List["LightBase"] = [], **kwargs):
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
        ensure( self.__nextGroupStartIndex + count  < self.lightCount, "not enough lights remaining" )
        self.__nextGroupStartIndex += count
        return rv
    
    def nextNLights(self, count:int, name:str=None, **kwargs ) ->NextNLights:
        return NextNLights( count=count,
                           name=name or f"{self.name}[{self.__nextGroupStartIndex}:{self.__nextGroupStartIndex+count-1}]", 
                           source=self,**kwargs )
    
    def lightChanged(self,light:"LightBase"): raise NotImplemented
    

#############################################################################
class LightBase(object):
    
    def __init__(self, source:LightSourceBase=None, index:int = 0):
        assert source is not None
        self.__source:LightSourceBase = source
        self.__sourceIndex:int = index
        
    @property
    def source(self)->LightSourceBase: return self.__source
    
    @property
    def sourceIndex(self)->int: return self.__sourceIndex
    
    def setValue(self,value:AnyLightValue, context: UpdateContext = None ):
        raise NotImplemented


class RGBLightBase(LightBase):
    pass


