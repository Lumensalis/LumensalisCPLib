from LumensalisCP.Lights.Values import *
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
#import LumensalisCP.Lights.LightBase as LightBase

from . import Light
#
#############################################################################

class LightGroup(NamedLocalIdentifiable):
    """ a group of related lights used for a common purpose

    Args:
        object (_type_): _description_
    """
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    @property
    def lightCount(self) -> int: raise NotImplemented
        
    @property
    def lights(self) -> Iterable["Light.Light"] : raise NotImplemented
    
    def __getitem__(self, index:int) -> "Light.Light": raise NotImplemented

    def __setitem__(self, index:int, value:AnyLightValue ): 
        self[index].setValue(value)
    
    def values(self,  context: Optional[EvaluationContext] = None ):
        context = UpdateContext.fetchCurrentContext(context)
        return [ light.getValue(context) for light in self.lights]
                
#############################################################################

class LightGroupList(LightGroup):
    def __init__(self, lights:List["Light.Light"] = [], name:Optional[str]=None,**kwargs):
        super().__init__(name=name,**kwargs)
        self.__lights:List["Light.Light"] = lights

    @property
    def lightCount(self) -> int: return len(self.__lights)
    
    @property
    def lights(self) -> Iterable["Light.Light"] :
        return iter(self.__lights)
    
    def __getitem__(self, index) -> "Light.Light":
        return self.__lights[index]

    def __setitem__(self, index, value:AnyLightValue ):
        self.__lights[index].setValue(value)

#############################################################################

class NextNLights(LightGroupList):
    def __init__(self,count:int,name:str, source:"LightSource",**kwargs):
        
        offset = source.startOfNextN(count)
        lights = list( [source[offset + index] for index in range(count)] )
        super().__init__(name=name,lights=lights,**kwargs)
        
class Ring(NextNLights): pass

class Stick(NextNLights): pass

class Strip(NextNLights): pass

#############################################################################

class AdHocLightGroup(LightGroupList):
    def __init__(self,name:str,**kwargs):
        self.__adHocLights = []
        super().__init__(name=name,lights=self.__adHocLights,**kwargs)
        
    def append(self, light:Light.Light|LightGroup):
        if isinstance(light, LightGroup):
            for l2 in light.lights:
                self.append(l2)
            return
        ensure( light not in self.__adHocLights, "light %s already in %s", light, self )
        self.__adHocLights.append( light )

#############################################################################

class LightSource(LightGroupList):
    """ driver / hardware interface providing Lights"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__nextGroupStartIndex = 0

    def startOfNextN(self, count:int ):
        rv = self.__nextGroupStartIndex 
        ensure( self.__nextGroupStartIndex + count  <= self.lightCount, "not enough lights remaining" )
        self.__nextGroupStartIndex += count
        return rv

    def _nextNLights(self, cls, count:int, name:Optional[str]=None, desc:Optional[str]=None, **kwargs ):
        return cls( count=count,
                           name=name or f"{desc}({self.name} [{self.__nextGroupStartIndex}:{self.__nextGroupStartIndex+count-1}])", 
                           source=self,**kwargs )
    
    def nextNLights(self, count:int, name:Optional[str]=None, **kwargs ) ->NextNLights:
        return self._nextNLights( NextNLights, count=count, name=name, **kwargs )
    
    def ring(self, count:int, name:Optional[str]=None, **kwargs ) -> Ring:
        return self._nextNLights( Ring, count=count, name=name, **kwargs )

    def stick(self, count:int, name:Optional[str]=None, **kwargs ) -> Stick:
        return self._nextNLights( Stick, count=count, name=name, **kwargs )

    def strip(self, count:int, name:Optional[str]=None, **kwargs ) -> Strip:
        return self._nextNLights( Strip, count=count, name=name, **kwargs )

    def single(self, name:Optional[str]=None, **kwargs ) ->NextNLights:
        return self._nextNLights( NextNLights, count=1, name=name, **kwargs )

    def lightChanged(self,light:"Light.Light"): raise NotImplemented

    
#############################################################################
