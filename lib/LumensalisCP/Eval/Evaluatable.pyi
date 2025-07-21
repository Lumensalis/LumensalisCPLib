from __future__ import annotations

# pylint: disable=unused-import,import-error,super-init-not-called,unused-private-member
# pylint: disable=unused-argument
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

from LumensalisCP.common import *
from LumensalisCP.Debug import Debuggable
from LumensalisCP.Main.Updates import UpdateContext, OptionalContextArg, DirectValue
if TYPE_CHECKING:
    #from LumensalisCP.Eval.Expressions import EvaluationContext
    from LumensalisCP.Lights.Values import RGB
    EVAL_VALUE_TYPES:TypeAlias  = Union[ int, float, bool, str, RGB]
    #class 
    #EvaluatableArg = TypeAlias  = Union[Evaluatable, DirectValue, EVAL_VALUE_TYPES]
    
#############################################################################
ET = TypeVar('ET' )
class Evaluatable[ET](Debuggable):
    def __init__(self): ...
    
    def getValue(self, context:OptionalContextArg) -> ET: ...
        

def evaluate[T]( value:T|Evaluatable[T], context:OptionalContextArg = None ) -> T: ...
