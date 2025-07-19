from .Values import *

from .Light import Light

#############################################################################

class LightGroup(NamedLocalIdentifiable):
    """ a group of related lights used for a common purpose

    Args:
        object (_type_): _description_
    """
    def __init__(self,**kwargs): ...
    
    @property
    def lightCount(self) -> int: ...
        
    @property
    def lights(self) -> Iterable[Light] : ...
    
    def __getitem__(self, index:int) -> Light: ...
    def __setitem__(self, index:int, value:AnyLightValue ): ...
    def values(self,  context: Optional[EvaluationContext] = None ) -> List[AnyLightValue]: ...

                
#############################################################################

class LightGroupList(LightGroup):
    def __init__(self, lights:List[Light] = [], name:Optional[str]=None,**kwargs): ...
    @property
    def lightCount(self) -> int: ...
    
    @property
    def lights(self) -> Iterable[Light] : ...
    
    def __getitem__(self, index) -> Light: ...
    def __setitem__(self, index, value:AnyLightValue ): ...

#############################################################################

class NextNLights(LightGroupList):
    def __init__(self,count:int,name:str, source:LightSource,**kwargs): ...

        
class Ring(NextNLights): pass

class Stick(NextNLights): pass

class Strip(NextNLights): pass

#############################################################################

class AdHocLightGroup(LightGroupList): 
    def __init__(self,name:str,**kwargs): ...
        
    def append(self, light:Light|LightGroup): ...

#############################################################################

class LightSource(LightGroupList):
    """ driver / hardware interface providing Lights"""
    def __init__(self, **kwargs): ...

    def startOfNextN(self, count:int ) -> int: ...
    
    def nextNLights(self, count:int, name:Optional[str]=None, **kwargs ) ->NextNLights: ...
    def ring(self, count:int, name:Optional[str]=None, **kwargs ) -> Ring: ...
    def stick(self, count:int, name:Optional[str]=None, **kwargs ) -> Stick: ...
    def strip(self, count:int, name:Optional[str]=None, **kwargs ) -> Strip: ...
    def single(self, name:Optional[str]=None, **kwargs ) ->NextNLights: ...

    def lightChanged(self,light:Light): ...

    
#############################################################################
