from __future__ import annotations

# pylint: disable=unused-import,import-error,unused-argument
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false
# pyright: reportUnknownVariableType=false

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import *
from LumensalisCP.Eval.Terms import *
from LumensalisCP.CPTyping import TYPE_CHECKING
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.Main.Refreshable import Refreshable
from LumensalisCP.Main.Updates import UpdateContext
from LumensalisCP.Eval.EvaluationContext  import EvaluationContext
from LumensalisCP.Eval.Evaluatable import evaluate, EvaluatableT, Evaluatable
from LumensalisCP.Eval.Expressions import Expression
from LumensalisCP.Eval.ExpressionTerm import ExpressionTerm, rising, EVAL_VALUE_TYPES
from LumensalisCP.util.kwCallback import KWCallback, KWCallbackArg
from LumensalisCP.Lights.RGB import RGB, AnyRGBValue

#_EvaluatableTimeInSecondsConfigArg:TypeAlias = Evaluatable


TimeInSecondsEvalArg:TypeAlias = Union[TimeInSecondsConfigArg, EvaluatableT[TimeInSeconds]]
TimeInSecondsEval:TypeAlias = Union[TimeInSeconds, float, EvaluatableT[TimeInSeconds]]

RGBConfigArg:TypeAlias = AnyRGBValue

# value or Evaluatable convertible to RGB
RGBEvalArg:TypeAlias = Union[AnyRGBValue, EvaluatableT[RGB]]

RGBEval:TypeAlias = Union[RGB, EvaluatableT[RGB]]


FloatEval:TypeAlias = Union[float, EvaluatableT[float]]    

def toTimeInSecondsEval(value:  TimeInSecondsEvalArg|None, default:Optional[TimeInSecondsEvalArg] = None) -> TimeInSecondsEval:
    if value is None: 
        value = default
        assert value is not None, "toTimeInSecondsEval requires a value or default"
    if isinstance(value, Evaluatable):
        return value # type: ignore
    return TimeInSeconds(value) # type: ignore


def toRGBEval(value:  RGBEvalArg) -> RGBEval:
    if isinstance(value, Evaluatable):
        return value # type: ignore
    return RGB.toRGB(value)
