from __future__ import annotations

# pylint: disable=unused-import,import-error,unused-argument
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false
# pyright: reportUnknownVariableType=false

from LumensalisCP.ImportProfiler import  getImportProfiler
__sayImport = getImportProfiler( __name__, globals() )

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import *
from LumensalisCP.Eval.Terms import *
#from LumensalisCP.CPTyping import TYPE_CHECKING
#from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.Temporal.Refreshable import Refreshable
from LumensalisCP.Main.Updates import UpdateContext
from LumensalisCP.Eval.EvaluationContext  import EvaluationContext
from LumensalisCP.Eval.Evaluatable import evaluate, EvaluatableT, Evaluatable
from LumensalisCP.Eval.Evaluatable import NamedEvaluatableProtocol, NamedEvaluatableProtocolT
from LumensalisCP.Eval.Expressions import Expression
from LumensalisCP.Eval.ExpressionTerm import ExpressionTerm, rising, EVAL_VALUE_TYPES
from LumensalisCP.util.kwCallback import KWCallback, KWCallbackArg
from LumensalisCP.Lights.RGB import *

__sayImport.parsing()

#_EvaluatableTimeInSecondsConfigArg:TypeAlias = Evaluatable

TimeInSecondsEvalArg:TypeAlias = Union[TimeInSecondsConfigArg, EvaluatableT[TimeInSeconds]]
TimeInSecondsEval:TypeAlias = Union[TimeInSeconds, float, EvaluatableT[TimeInSeconds]]

def toTimeInSecondsEval(value:  TimeInSecondsEvalArg|None, default:Optional[TimeInSecondsEvalArg] = None) -> TimeInSecondsEval:
    if value is None: 
        value = default
        assert value is not None, "toTimeInSecondsEval requires a value or default"
    if isinstance(value, Evaluatable):
        return value # type: ignore
    return TimeInSeconds(value) # type: ignore

RGBConfigArg:TypeAlias = AnyRGBValue

# value or Evaluatable convertible to RGB
RGBEvalArg:TypeAlias = Union[AnyRGBValue, EvaluatableT[RGB]]

RGBEval:TypeAlias = Union[RGB, EvaluatableT[RGB]]


def toRGBEval(value:  RGBEvalArg) -> RGBEval:
    if isinstance(value, Evaluatable):
        return value # type: ignore
    return RGB.toRGB(value)


FloatEvalArg:TypeAlias = Union[float, EvaluatableT[float]]    
FloatEval:TypeAlias = Union[float, EvaluatableT[float]]   

def toFloatEval(value:  FloatEvalArg|None, default:Optional[FloatEvalArg] = None) -> FloatEval:
    if value is None: 
        value = default
        assert value is not None, "toFloatEval requires a value or default"
    if isinstance(value, Evaluatable):
        return value # type: ignore
    return float(value) # type: ignore


PlusMinusOneEvalArg:TypeAlias = Union[PlusMinusOne, EvaluatableT[PlusMinusOne]]
PlusMinusOneEval:TypeAlias = Union[PlusMinusOne, EvaluatableT[PlusMinusOne]]

def toPlusMinusOne(value:  PlusMinusOneEvalArg|None, default:Optional[PlusMinusOneEvalArg] = None) -> PlusMinusOne:
    if value is None: 
        value = default
        assert value is not None, "toPlusMinusOne requires a value or default"
    if isinstance(value, Evaluatable):
        value = UpdateContext.fetchCurrentContext(None).valueOf(value)
    return PlusMinusOne(value) # type: ignore

def toPlusMinusOneEval(value:  PlusMinusOneEvalArg|None, default:Optional[PlusMinusOneEvalArg] = None) -> PlusMinusOneEval:
    if value is None: 
        value = default
        assert value is not None, "toPlusMinusOneEval requires a value or default"
    if isinstance(value, Evaluatable):
        return value # type: ignore
    return PlusMinusOne(value) # type: ignore

ZeroToOneEvalArg:TypeAlias = Union[ZeroToOne, EvaluatableT[ZeroToOne]]
ZeroToOneEval:TypeAlias = Union[ZeroToOne, EvaluatableT[ZeroToOne]]

def toZeroToOneEval(value:  ZeroToOneEvalArg|None, default:Optional[ZeroToOneEvalArg] = None) -> ZeroToOneEval:
    if value is None: 
        value = default
        assert value is not None, "toZeroToOneEval requires a value or default"
    if isinstance(value, Evaluatable):
        return value # type: ignore
    return ZeroToOne(value) # type: ignore


__sayImport.complete()
