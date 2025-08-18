from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayEvalEvaluatableImport = getImportProfiler( globals() ) # "Eval.Evaluatable"

from LumensalisCP.common import Debuggable,TypeVar, Generic, GenericT, TYPE_CHECKING, Any, Iterable, Protocol
#from LumensalisCP.Debug import Debuggable
from LumensalisCP.Main.Updates import UpdateContext, OptionalContextArg, DirectValue


#############################################################################

_sayEvalEvaluatableImport.parsing()

ET = TypeVar('ET',covariant=True) 


   
if TYPE_CHECKING:
    class NamedEvaluatableProtocol(Protocol, Generic[ET]):
        @property
        def name(self) -> str: ...
        def getValue(self, context:OptionalContextArg) -> ET:
            """ current value of term"""
            raise NotImplementedError
        
else:
    class NamedEvaluatableProtocol: ...

NamedEvaluatableProtocolT = GenericT(NamedEvaluatableProtocol)
    


class Evaluatable(Debuggable, Generic[ET]):
    
    def __init__(self):
        super().__init__()
        self.enableDbgEvaluate = False
    
    def __class_getitem__(cls, item:Any): # type: ignore
        return cls
        
    def getValue(self, context:OptionalContextArg) -> ET:
        """ current value of term"""
        raise NotImplementedError
    
    def dependencies(self) -> Iterable[Evaluatable[ET]]:
        raise NotImplementedError
    
if TYPE_CHECKING:
    EvaluatableT = Evaluatable
else:
    class _EvaluatableT:
        def __class_getitem__(cls, item): # pylint: disable=unused-argument
            return Evaluatable
        def __getitem__(self, item): # pylint: disable=unused-argument
            return Evaluatable        
    #EvaluatableT = _EvaluatableT()
    EvaluatableT = GenericT(Evaluatable)
        
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
