from __future__ import annotations

# pylint: disable=unused-argument, super-init-not-called, unused-private-member

from LumensalisCP.common import *

from LumensalisCP.Identity.Local import *
from LumensalisCP.Main.Refreshable import Refreshable
from LumensalisCP.Main.Updates import UpdateContext
from LumensalisCP.Eval.EvaluationContext  import EvaluationContext
from LumensalisCP.Eval.Expressions import Expression
from LumensalisCP.Eval.Evaluatable import evaluate, Evaluatable
from LumensalisCP.Eval.ExpressionTerm import ExpressionTerm
#from LumensalisCP.Eval.Evaluatable import DirectValue
from LumensalisCP.Eval.Terms import *

from LumensalisCP.util.bags import Bag
from LumensalisCP.util.kwCallback import KWCallback
from LumensalisCP.Lights.Values import RGB, AnyLightValue, LightValueRGB

_EvaluatableTimeInSecondsConfigArg:TypeAlias = Evaluatable[TimeInSecondsConfigArg]

TimeInSecondsEvalArg:TypeAlias = Union[TimeInSecondsConfigArg, Evaluatable[TimeInSecondsConfigArg]]
TimeInSecondsEval:TypeAlias = Union[TimeInSeconds, Evaluatable[TimeInSeconds]]
def toTimeInSecondsEval(value:  TimeInSecondsEvalArg|None, default:Optional[TimeInSecondsEvalArg] = None) -> TimeInSecondsEval:...

RGBConfigArg:TypeAlias = AnyLightValue
RGBEvalArg:TypeAlias = Union[AnyLightValue, Evaluatable[RGB]]
RGBEval:TypeAlias = Union[RGB, Evaluatable[RGB]]
def toRGBEval(value:  RGBEvalArg) -> RGBEval: ...
