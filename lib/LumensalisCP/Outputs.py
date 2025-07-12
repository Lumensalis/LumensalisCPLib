from LumensalisCP.Main.Expressions import *
from LumensalisCP.Inputs import InputSource

#############################################################################

class OutputTarget(object):

    def __init__(self, name:str = None):
        if name is not None:
            self.__name = name = name
        
    def set( self, value:Any, context:EvaluationContext ):
        raise NotImplemented
    
    @property
    def name(self): return getattr( self, '__OutputTarget__name', None ) or f"{self.__class__.__name__}_{id(self)}"
    
class NamedOutputTarget(NamedLocalIdentifiable,OutputTarget):

    def __init__(self, name:str = None):
        super().__init__(name=name)
        OutputTarget.__init__(self)

    def set( self, value:Any, context:EvaluationContext ):
        raise NotImplemented

    def path( self ): return None
    
    
    
__all__ = [ OutputTarget, NamedOutputTarget ]