from __future__ import annotations

from LumensalisCP.common import Optional, Any
from LumensalisCP.Lights.Groups import LightSource
from LumensalisCP.Lights.RGB import RGB, AnyRGBValue
from LumensalisCP.Lights.Values import LightValueBase
from LumensalisCP.Outputs import OutputTarget
from LumensalisCP.Eval.EvaluationContext import EvaluationContext

#############################################################################

class LightType:
    LT_SINGLE_SOLID=1
    LT_SINGLE_DIMMABLE=3
    LT_RGB=4
    
    #LT_TYPES = Required[ LT_SINGLE_SOLID | LT_SINGLE_DIMMABLE | LT_RGB ]
    
#############################################################################
class Light(OutputTarget):
    
    def __init__(self, source:LightSource, index:int = 0, name:Optional[str] = None):
        super().__init__(name=name)
        assert source is not None
        self.__source:LightSource = source
        self.__sourceIndex:int = index
        
    @property
    def source(self)->LightSource: return self.__source
    
    @property
    def sourceIndex(self)->int: return self.__sourceIndex
    
    def setValue(self,value:AnyRGBValue, context: Optional[EvaluationContext] = None ) -> None:
        raise NotImplementedError

    def set( self, value:Any, context:EvaluationContext ):
        self.setValue( value, context )
    
    @property
    def value(self): return self.getValue()
    
    def getValue(self, context: Optional[EvaluationContext] = None ) -> AnyRGBValue:
        raise NotImplementedError
    
    def getLightValue(self)-> LightValueBase: raise NotImplementedError  
    
    def getRGB(self):
        return self.getLightValue().asRGB
    
    @property
    def lightType(self)->int: raise NotImplementedError  

#############################################################################
class SolidLight(Light): # pylint: disable=abstract-method
    """ for regular single color LEDs"""
    
    @property
    def lightType(self): return LightType.LT_SINGLE_SOLID

#############################################################################
class DimmableLight(Light): # pylint: disable=abstract-method
    """ for regular single color LEDs"""
    
    @property
    def lightType(self): return LightType.LT_SINGLE_DIMMABLE
    
#############################################################################
class RGBLight(Light): # pylint: disable=abstract-method
    @property
    def lightType(self): return LightType.LT_RGB

#############################################################################

__all__ = [
    "LightType",
    "Light",
    "SolidLight",
    "DimmableLight",
    "RGBLight", 
    "AnyRGBValue",
    "RGB",  
]
