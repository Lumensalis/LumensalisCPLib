
from LumensalisCP.ImportProfiler import  getImportProfiler
_sayOutputsImport = getImportProfiler( globals() ) # "Outputs"


from LumensalisCP.Eval.Expressions import *

#############################################################################

_sayOutputsImport.parsing()

class OutputTarget(CountedInstance):

    def __init__(self, name:Optional[str] = None):
        super().__init__()
        
    def set( self, value:Any, context:EvaluationContext ) -> None:
        raise NotImplementedError
    
    
class NamedOutputTarget(NamedLocalIdentifiable,OutputTarget):

    def __init__(self, **kwds:Unpack[NamedLocalIdentifiable.KWDS]):
        NamedLocalIdentifiable.__init__(self,**kwds)
        OutputTarget.__init__(self)

    @override
    def set( self, value:Any, context:EvaluationContext ) -> None:
        raise NotImplementedError

    def path( self ): return None

_sayOutputsImport.complete(globals())
    
__all__ = [ 'OutputTarget', 'NamedOutputTarget' ]
