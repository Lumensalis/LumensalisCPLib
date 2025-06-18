from .Groups import *

#############################################################################

class LightType:
    LT_SINGLE_SOLID=1
    LT_SINGLE_DIMMABLE=3
    LT_RGB=4
    
    #LT_TYPES = Required[ LT_SINGLE_SOLID | LT_SINGLE_DIMMABLE | LT_RGB ]
    
#############################################################################
class Light(OutputTarget):
    
    def __init__(self, source:LightSource=None, index:int = 0, name:str|None = None):
        super().__init__(name=name)
        assert source is not None
        self.__source:LightSource = source
        self.__sourceIndex:int = index
        
    @property
    def source(self)->LightSource: return self.__source
    
    @property
    def sourceIndex(self)->int: return self.__sourceIndex
    
    def setValue(self,value:AnyLightValue, context: UpdateContext = None ):
        raise NotImplemented

    def set( self, value:Any, context:UpdateContext ):
        self.setValue( value, context )
    
    @property
    def value(self): return self.getValue()
    
    def getValue(self, context: UpdateContext = None ) -> AnyLightValue:
        raise NotImplemented
    
    def getLightValue(self)-> LightValueBase: raise NotImplemented  
    
    def getRGB(self):
        return self.getLightValue().asRGB
    
    @property
    def lightType(self): raise NotImplemented  

#############################################################################
class SolidLight(Light):
    """ for regular single color LEDs"""
    
    @property
    def lightType(self): return LightType.LT_SINGLE_SOLID

#############################################################################
class DimmableLight(Light):
    """ for regular single color LEDs"""
    
    @property
    def lightType(self): return LightType.LT_SINGLE_DIMMABLE
    
#############################################################################
class RGBLight(Light):
    @property
    def lightType(self): return LightType.LT_RGB

#############################################################################
