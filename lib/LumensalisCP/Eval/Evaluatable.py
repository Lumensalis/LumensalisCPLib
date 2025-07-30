from __future__ import annotations

from LumensalisCP.Main.PreMainConfig import pmc_getImportProfiler
_sayEvalEvaluatableImport = pmc_getImportProfiler( "Eval.Evaluatable" )

from LumensalisCP.common import Debuggable,TypeVar, Generic, TYPE_CHECKING, Any
#from LumensalisCP.Debug import Debuggable
from LumensalisCP.Main.Updates import UpdateContext, OptionalContextArg, DirectValue
   
    
#############################################################################

_sayEvalEvaluatableImport.parsing()

ET = TypeVar('ET' )


class Evaluatable(Debuggable, Generic[ET]):
    
    def __init__(self):
        super().__init__()
        self.enableDbgEvaluate = False
    
    def __class_getitem__(cls, item:Any): # type: ignore
        return cls
        
    def getValue(self, context:OptionalContextArg) -> ET:
        """ current value of term"""
        raise NotImplementedError
    
if TYPE_CHECKING:
    EvaluatableT = Evaluatable
else:
    class _EvaluatableT:
        def __class_getitem__(cls, item): # pylint: disable=unused-argument
            return Evaluatable
        def __getitem__(self, item): # pylint: disable=unused-argument
            return Evaluatable        
    EvaluatableT = _EvaluatableT()
        
def evaluate( value:Evaluatable[DirectValue]|DirectValue, context:OptionalContextArg = None ):
    if isinstance( value, Evaluatable ):
        context = UpdateContext.fetchCurrentContext(context)
        if  context.debugEvaluate or value.enableDbgEvaluate:
            with context.nestDebugEvaluate() as nde:
                rv = value.getValue(context)
                nde.say(value, "evaluate returning %r", rv)
            return rv
        else:
            return value.getValue(context)
    
    return value

_sayEvalEvaluatableImport.complete(globals())
