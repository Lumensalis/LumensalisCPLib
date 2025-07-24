from __future__ import annotations
# pylint: disable=unused-argument, super-init-not-called, unused-private-member

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import *
from LumensalisCP.Lights.RGB import *
from LumensalisCP.Eval.Terms import *
from LumensalisCP.Main.Refreshable import Refreshable
from LumensalisCP.Main.Updates import UpdateContext
from LumensalisCP.Eval.EvaluationContext  import EvaluationContext
from LumensalisCP.Eval.Evaluatable import evaluate, Evaluatable
from LumensalisCP.Eval.Expressions import Expression
from LumensalisCP.Eval.ExpressionTerm import ExpressionTerm, rising
from LumensalisCP.util.kwCallback import KWCallback, KWCallbackArg

from LumensalisCP.Lights.Values import LightValueRGB
from LumensalisCP.util.bags import Bag

_EvaluatableTimeInSecondsConfigArg:TypeAlias = Evaluatable[TimeInSecondsConfigArg]

TimeInSecondsEvalArg:TypeAlias = Union[TimeInSecondsConfigArg, Evaluatable[TimeInSecondsConfigArg]]
TimeInSecondsEval:TypeAlias = Union[TimeInSeconds, float, Evaluatable[TimeInSeconds]]

RGBConfigArg:TypeAlias = AnyRGBValue
RGBEvalArg:TypeAlias = Union[AnyRGBValue, Evaluatable[RGB]]


type RGBEval = Union[RGB, Evaluatable[RGB]] # value or Evaluatable convertible to RGB 
""" TypeAlias: value or Evaluatable convertible to RGB 
"""

FloatEval:TypeAlias = Union[float, Evaluatable[float]]
def toTimeInSecondsEval(value:  TimeInSecondsEvalArg|None, default:Optional[TimeInSecondsEvalArg] = None) -> TimeInSecondsEval:...
def toRGBEval(value:  RGBEvalArg) -> RGBEval: ...
