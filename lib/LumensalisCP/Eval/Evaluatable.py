from LumensalisCP.common import *
from LumensalisCP.Debug import Debuggable
from LumensalisCP.Main.Updates import UpdateContext, OptionalContextArg, DirectValue

if TYPE_CHECKING:
    #from LumensalisCP.Eval.Expressions import EvaluationContext
    from LumensalisCP.Lights.Values import RGB
    EVAL_VALUE_TYPES:TypeAlias  = Union[ int, float, bool, str, RGB]
    
    
#############################################################################
ET = TypeVar('ET' )


class Evaluatable(Debuggable, Generic[ET]):
    def __init__(self):
        super().__init__()
        self.enableDbgEvaluate = False
    
    def getValue(self, context:OptionalContextArg) -> ET:
        """ current value of term"""
        raise NotImplementedError

def evaluate( value:Evaluatable|DirectValue, context:OptionalContextArg = None ):
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
