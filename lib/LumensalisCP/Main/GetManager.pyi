

from LumensalisCP.util.Singleton import Singleton

from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Eval.EvaluationContext import EvaluationContext

getMainManager = Singleton[MainManager] ("MainManager")

def getCurrentEvaluationContext() -> EvaluationContext: ...


__all__ = [
    "getCurrentEvaluationContext",
    "getMainManager"
]
