from __future__ import annotations

import math
from LumensalisCP.Main.PreMainConfig import ImportProfiler
_ioContextImport = ImportProfiler( "IOContext" )

from LumensalisCP.common import *
from LumensalisCP.Eval.common import *
from LumensalisCP.common import TYPE_CHECKING
from LumensalisCP.Identity.Local import NamedLocalIdentifiable

_ioContextImport( "Inputs")
from LumensalisCP.Inputs import InputSource
from LumensalisCP.Outputs import OutputTarget, NamedOutputTarget
from LumensalisCP.Eval.Expressions  import Expression
from LumensalisCP.Eval.ExpressionTerm import ExpressionTerm, EVAL_VALUE_TYPES, rising

from LumensalisCP.CPTyping import TYPE_CHECKING
if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    # shouldn't be needed, but pyright whines and misses 
    # them in `from LumensalisCP.Eval.common import *`
    from LumensalisCP.Debug import Debuggable
    from LumensalisCP.util.kwCallback import KWCallback, KWCallbackArg
    from LumensalisCP.Debug import Debuggable
    from LumensalisCP.Eval.EvaluationContext import EvaluationContext
    from LumensalisCP.Eval.Evaluatable import evaluate, Evaluatable
    from LumensalisCP.Main.Updates import UpdateContext

_ioContextImport( "complete.")