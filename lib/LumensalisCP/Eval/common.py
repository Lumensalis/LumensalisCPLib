from __future__ import annotations
from LumensalisCP.common import *

from LumensalisCP.Identity.Local import *
from LumensalisCP.Eval.Terms import *
from LumensalisCP.Main.Refreshable import Refreshable
from LumensalisCP.Main.Updates import UpdateContext
from LumensalisCP.Eval.EvaluationContext  import EvaluationContext
from LumensalisCP.Eval.Evaluatable import evaluate, Evaluatable
from LumensalisCP.Eval.Expressions import Expression
from LumensalisCP.Eval.ExpressionTerm import ExpressionTerm, rising
from LumensalisCP.util.kwCallback import KWCallback

from LumensalisCP.Lights.Values import RGB, AnyLightValue, LightValueRGB

#_EvaluatableTimeInSecondsConfigArg:TypeAlias = Evaluatable

TimeInSecondsEvalArg:TypeAlias = Union[TimeInSecondsConfigArg, Evaluatable]
TimeInSecondsEval:TypeAlias = Union[TimeInSeconds, Evaluatable]
def toTimeInSecondsEval(value:  TimeInSecondsEvalArg|None, default:Optional[TimeInSecondsEvalArg] = None) -> TimeInSecondsEval:
    if value is None: 
        value = default
        assert value is not None, "toTimeInSecondsEval requires a value or default"
    if isinstance(value, Evaluatable):
        return value # type: ignore
    return TimeInSeconds(value) # type: ignore

RGBConfigArg:TypeAlias = AnyLightValue
RGBEvalArg:TypeAlias = Union[AnyLightValue, Evaluatable]
RGBEval:TypeAlias = Union[RGB, Evaluatable]

def toRGBEval(value:  RGBEvalArg) -> RGBEval:
    if isinstance(value, Evaluatable):
        return value # type: ignore
    return LightValueRGB.toRGB(value)
