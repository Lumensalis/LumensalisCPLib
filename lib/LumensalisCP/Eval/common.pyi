from __future__ import annotations
# pylint: disable=unused-argument, super-init-not-called, unused-private-member

# pyright: reportUnusedImport=false

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import *
from LumensalisCP.Lights.RGB import *
from LumensalisCP.Eval.Terms import *
from LumensalisCP.Main.Updates import UpdateContext
from LumensalisCP.Eval.EvaluationContext  import EvaluationContext
from LumensalisCP.Eval.Evaluatable import evaluate, Evaluatable, EvaluatableT
from LumensalisCP.Eval.Evaluatable import NamedEvaluatableProtocol, NamedEvaluatableProtocolT
from LumensalisCP.Eval.Expressions import Expression
from LumensalisCP.Eval.ExpressionTerm import ExpressionTerm, rising
from LumensalisCP.util.kwCallback import KWCallback, KWCallbackArg

from LumensalisCP.Lights.Values import LightValueRGB
from LumensalisCP.util.bags import Bag

_EvaluatableTimeInSecondsConfigArg:TypeAlias = Evaluatable[TimeInSecondsConfigArg]

TimeInSecondsEvalArg:TypeAlias = Union[TimeInSecondsConfigArg, Evaluatable[TimeInSecondsConfigArg]]
TimeInSecondsEval:TypeAlias = Union[TimeInSeconds, float, Evaluatable[TimeInSeconds]]

RGBConfigArg:TypeAlias = AnyRGBValue

type RGBEval = Union[RGB, Evaluatable[RGB]] # value or Evaluatable convertible to RGB 
""" TypeAlias: value or Evaluatable convertible to RGB 
"""

RGBEvalArg:TypeAlias = Union[AnyRGBValue, Evaluatable[RGB]]
def toRGBEval(value:  RGBEvalArg) -> RGBEval: ...


FloatEval:TypeAlias = Union[float, Evaluatable[float]]
FloatEvalArg:TypeAlias = Union[float, Evaluatable[float]]
ZeroToOneEval:TypeAlias = Union[ZeroToOne, Evaluatable[ZeroToOne]]
ZeroToOneEvalArg:TypeAlias = Union[ZeroToOne, Evaluatable[ZeroToOne]]



def toTimeInSecondsEval(value: Optional[TimeInSecondsEvalArg] = None, default:Optional[TimeInSecondsEvalArg] = None) -> TimeInSecondsEval:...
def toFloatEval(value: Optional[FloatEvalArg] = None, default:Optional[FloatEvalArg] = None) -> FloatEval: ...
def toZeroToOneEval(value: Optional[ZeroToOneEvalArg] = None, default:Optional[ZeroToOneEvalArg] = None) -> ZeroToOneEval: ...

PlusMinusOneEval:TypeAlias = Union[PlusMinusOne, Evaluatable[PlusMinusOne]]
PlusMinusOneEvalArg:TypeAlias = Union[PlusMinusOne, Evaluatable[PlusMinusOne]]

def toPlusMinusOne(value: Optional[PlusMinusOneEvalArg] = None, default:Optional[PlusMinusOneEvalArg] = None) -> PlusMinusOne: ...
def toPlusMinusOneEval(value: Optional[PlusMinusOneEvalArg] = None, default:Optional[PlusMinusOneEvalArg] = None) -> PlusMinusOneEval: ...
