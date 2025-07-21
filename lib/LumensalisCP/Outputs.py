from LumensalisCP.Eval.Expressions import *
from LumensalisCP.Inputs import InputSource

#############################################################################

class OutputTarget(object):

    def __init__(self, name:Optional[str] = None):
        pass
        
    def set( self, value:Any, context:EvaluationContext ) -> None:
        raise NotImplementedError
    
    
class NamedOutputTarget(NamedLocalIdentifiable,OutputTarget):

    def __init__(self, name:Optional[str] = None):
        NamedLocalIdentifiable.__init__(self, name=name)
        OutputTarget.__init__(self)

    @override
    def set( self, value:Any, context:EvaluationContext ) -> None:
        raise NotImplementedError

    def path( self ): return None

    
__all__ = [ 'OutputTarget', 'NamedOutputTarget', 'KWDS_NamedOutputTarget' ]
