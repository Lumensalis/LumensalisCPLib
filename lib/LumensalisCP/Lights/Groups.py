from __future__ import annotations

# pyright: reportUnusedImport=false

#from LumensalisCP.common import Optional, Any, Iterable, List, TYPE_CHECKING, ensure
from LumensalisCP.common import *
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.Main.Updates import UpdateContext
from LumensalisCP.Lights.RGB import RGB, AnyRGBValue
from LumensalisCP.Lights.Values import LightValueBase
from LumensalisCP.Outputs import OutputTarget
from LumensalisCP.Eval.EvaluationContext import EvaluationContext

if TYPE_CHECKING:
    from LumensalisCP.Lights.Light import Light
#
#############################################################################

class LightGroup(NamedLocalIdentifiable):
    """ a group of related lights used for a common purpose

    Args:
        object (_type_): _description_
    """
    def __init__(self,**kwargs:Unpack[NamedLocalIdentifiable.KWDS]):
        super().__init__(**kwargs)

    @property
    def lightCount(self) -> int: raise NotImplementedError
        
    @property
    def lights(self) -> Iterable[Light] : raise NotImplementedError
    
    def __getitem__(self, index:int) -> Light: raise NotImplementedError


    def __setitem__(self, index:int, value:AnyRGBValue ): 
        self[index].setValue(value)
    
    def values(self,  context: Optional[EvaluationContext] = None ):
        context = UpdateContext.fetchCurrentContext(context)
        return [ light.getValue(context) for light in self.lights]
                
#############################################################################

class LightGroupList(LightGroup):
    
    class KWDS(NamedLocalIdentifiable.KWDS):
        lights: NotRequired[List[Light]] 
        
    def __init__(self, lights:List[Light]|None = None,**kwargs:Unpack[NamedLocalIdentifiable.KWDS]):
        super().__init__(**kwargs)
        assert lights is not None
        self.__lights:List[Light] = lights

    @property
    def lightCount(self) -> int: return len(self.__lights)
    
    @property
    def lights(self) -> Iterable[Light] :
        return iter(self.__lights)
    
    def __getitem__(self, index:int) -> Light:
        return self.__lights[index]

    def __setitem__(self, index:int, value:AnyRGBValue ):
        self.__lights[index].setValue(value)

#############################################################################

class NextNLights(LightGroupList):
    def __init__(self,count:int, source:"LightSource",**kwargs:Unpack[LightGroupList.KWDS] ):
        
        offset = source.startOfNextN(count)
        assert "lights" not in kwargs, "cannot specify lights for NextNLights"
        kwargs['lights'] = list( [source[offset + index] for index in range(count)] )
        super().__init__(**kwargs)
        
class Ring(NextNLights): pass

class Stick(NextNLights): pass

class Strip(NextNLights): pass

#############################################################################

class AdHocLightGroup(LightGroupList):
    def __init__(self,**kwargs:Unpack[LightGroupList.KWDS]):
        self.__adHocLights:List[Light] = kwargs.get('lights', [])
        kwargs['lights'] = self.__adHocLights
        super().__init__(**kwargs)
        
    def append(self, light:Light|LightGroup):
        if isinstance(light, LightGroup):
            for l2 in light.lights:
                self.append(l2)
            return
        ensure( light not in self.__adHocLights, "light %s already in %s", light, self )
        self.__adHocLights.append( light )

#############################################################################

class LightSource(LightGroupList):
    """ driver / hardware interface providing Lights"""
    
    KWDS = LightGroupList.KWDS
    
    def __init__(self, **kwargs:Unpack[LightGroupList.KWDS]):
        super().__init__(**kwargs)
        self.__nextGroupStartIndex = 0

    def startOfNextN(self, count:int ):
        rv = self.__nextGroupStartIndex 
        assert  self.__nextGroupStartIndex + count  <= self.lightCount, (
            f"not enough lights remaining for {count} more ({self.__nextGroupStartIndex} of {self.lightCount} used in ({self.__class__.__name__}){self.name} )"
        )
        self.__nextGroupStartIndex += count
        return rv

    def _nextNLights(self, cls:Any, count:int, **kwargs:StrAnyDict ):
        
        return cls( count=count,
                           #name=name or f"{desc}({self.name} [{self.__nextGroupStartIndex}:{self.__nextGroupStartIndex+count-1}])", 
                           source=self,**kwargs )
    
    def nextNLights(self, count:int, **kwargs:dict[str,Any] ) ->NextNLights:
        return self._nextNLights( NextNLights, count=count,  **kwargs )
    
    def ring(self, count:int, **kwargs:StrAnyDict ) -> Ring:
        return self._nextNLights( Ring, count=count, **kwargs )

    def stick(self, count:int,  **kwargs:StrAnyDict ) -> Stick:
        return self._nextNLights( Stick, count=count, **kwargs )

    def strip(self, count:int,  **kwargs:StrAnyDict ) -> Strip:
        return self._nextNLights( Strip, count=count, **kwargs )

    def single(self,  **kwargs:StrAnyDict  ) ->NextNLights:
        return self._nextNLights( NextNLights, count=1, **kwargs )

    def lightChanged(self,light:Light) -> None: 
        raise NotImplementedError

    
#############################################################################

__all__ = [
    "LightGroup",
    "LightGroupList",
    "NextNLights",
    "Ring",
    "Stick",
    "Strip",
    "AdHocLightGroup",
    "LightSource",
]
