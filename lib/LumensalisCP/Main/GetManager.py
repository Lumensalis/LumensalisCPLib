

from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayMainGetManagerImport = getImportProfiler( globals() ) # "Main.GetManager"

from LumensalisCP.CPTyping import TYPE_CHECKING

from LumensalisCP.util.Singleton import Singleton

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    from LumensalisCP.Updates import UpdateContext
    from LumensalisCP.Eval.EvaluationContext import EvaluationContext
    
getMainManager:Singleton[MainManager] = Singleton("MainManager") # type: ignore

def getCurrentEvaluationContext() -> EvaluationContext:
    return getMainManager().getContext()

__all__ = [
    "getCurrentEvaluationContext",
    "getMainManager"
]


_sayMainGetManagerImport.complete(globals())
