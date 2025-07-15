from LumensalisCP.Main.Expressions import *
from LumensalisCP.Inputs import InputSource

#############################################################################

class OutputTarget(object):

    def __init__(self, name:str = None):
        pass
        
    def set( self, value:Any, context:EvaluationContext ):
        raise NotImplemented
    
    
class NamedOutputTarget(NamedLocalIdentifiable,OutputTarget):

    def __init__(self, name:str = None):
        NamedLocalIdentifiable.__init__(self, name=name)
        OutputTarget.__init__(self)

    def set( self, value:Any, context:EvaluationContext ):
        raise NotImplemented

    def path( self ): return None
    
    
    
__all__ = [ OutputTarget, NamedOutputTarget ]