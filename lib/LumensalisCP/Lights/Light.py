from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler
__profileImport = getImportProfiler(__name__,globals())

#############################################################################

from LumensalisCP.common import Optional, Any, Unpack, NotRequired
from LumensalisCP.Lights.Groups import LightSource, LightGroup
from LumensalisCP.Lights.RGB import *

from LumensalisCP.Lights.Values import LightValueBase
from LumensalisCP.Outputs import NamedOutputTarget
from LumensalisCP.Eval.EvaluationContext import EvaluationContext

#############################################################################

__profileImport.parsing()

class LightType:
    LT_SINGLE_SOLID=1
    LT_SINGLE_DIMMABLE=3
    LT_RGB=4
    
    #LT_TYPES = Required[ LT_SINGLE_SOLID | LT_SINGLE_DIMMABLE | LT_RGB ]
    
#############################################################################
class Light(NamedOutputTarget):

    class KWDS(NamedOutputTarget.KWDS):
        name: NotRequired[str]
        source: NotRequired[LightSource]
        index: NotRequired[int]

    def __init__(self, source:LightSource, index:int = 0, **kwds:Unpack[NamedOutputTarget.KWDS]) -> None:
        super().__init__(**kwds)
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
    "LightSource",
    "LightGroup"
]

__profileImport.complete()
