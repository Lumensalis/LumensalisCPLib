from .Values import *

#import LumensalisCP.Lights.LightBase as LightBase
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
    def lights(self) -> Iterable["LightBase.Light"] : raise NotImplemented
    
    def __getitem__(self, index:int) -> "LightBase.Light": raise NotImplemented

    def __setitem__(self, index:int, value:AnyLightValue ): 
        self[index].setValue(value)
    
    def values(self,  context: UpdateContext = None ):
        return [ light.getValue(context) for light in self.lights]
                
#############################################################################

class LightGroupList(LightGroup):
    def __init__(self, lights:List["LightBase.Light"] = [], name:str|None=None,**kwargs):
        super().__init__(name=name,**kwargs)
        self.__lights:List["LightBase.Light"] = lights

    @property
    def lightCount(self) -> int: return len(self.__lights)
    
    @property
    def lights(self) -> Iterable["LightBase.Light"] :
        return iter(self.__lights)
    
    def __getitem__(self, index) -> "LightBase.Light":
        return self.__lights[index]

    def __setitem__(self, index, value:AnyLightValue ):
        self.__lights[index].setValue(value)

#############################################################################

class NextNLights(LightGroupList):
    def __init__(self,count:int,name:str, source:"LightSource",**kwargs):
        
        offset = source.startOfNextN(count)
        lights = list( [source[offset + index] for index in range(count)] )
        super().__init__(name=name,lights=lights,**kwargs)

#############################################################################

class AdHocLightGroup(LightGroupList):
    def __init__(self,name:str,**kwargs):
        self.__adHocLights = []
        super().__init__(name=name,lights=self.__adHocLights,**kwargs)
        
    def append(self, light:"LightBase.Light"|LightGroup):
        if isinstance(light, LightGroup):
            for l2 in LightGroup.lights:
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
    
    def nextNLights(self, count:int, name:str=None, **kwargs ) ->NextNLights:
        return NextNLights( count=count,
                           name=name or f"{self.name}[{self.__nextGroupStartIndex}:{self.__nextGroupStartIndex+count-1}]", 
                           source=self,**kwargs )
    
    def lightChanged(self,light:"LightBase.Light"): raise NotImplemented

    
#############################################################################
