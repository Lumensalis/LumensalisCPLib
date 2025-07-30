from __future__ import annotations

from LumensalisCP.Main.PreMainConfig import ImportProfiler
_sayInvocableImport = ImportProfiler( "Triggers.Invocable" )

#from LumensalisCP.Debug import Debuggable

from LumensalisCP.CPTyping import *
from LumensalisCP.Identity.Local import NamedLocalIdentifiable

if TYPE_CHECKING:
    from LumensalisCP.Eval.EvaluationContext import EvaluationContext


# invocable
class Invocable:
    """
    """
    
    def tName(self) -> str:
        return getattr(self,'dbgName',None) or f"{self.__class__.__name__}@{id(self):X}"

    def invoke(self, context: EvaluationContext) -> None:
        raise NotImplemented

    def __call__(self, context: EvaluationContext) -> None:
        self.invoke(context)

    @classmethod
    def make(cls, what:Any) -> Invocable:
        if isinstance(what, Invocable):
            return what
        raise TypeError(f"Cannot convert {type(what)} to Invocable")
    
    @classmethod
    def makeInvocable(cls, what:InvocableOrContextCB) -> 'Invocable':
        return InvocableContextCB.make(what)
    
    @classmethod
    def makeContextInvocable(cls, what:InvocableOrContextCB) -> 'Invocable':
        return InvocableContextCB.make(what)

    @classmethod
    def makeSimpleInvocable(cls, what:InvocableOrSimpleCB) -> 'Invocable':
        return InvocableSimpleCB.make(what)

class NamedInvocable(NamedLocalIdentifiable, Invocable):

    def __init__(self, **kwds:Unpack[NamedLocalIdentifiable.KWDS]) -> None:
        NamedLocalIdentifiable.__init__(self,**kwds)

class InvocableSimpleCB(NamedInvocable):
    """
    """
    def __init__(self, cb:Callable[[], None], **kwds:Unpack[NamedLocalIdentifiable.KWDS]) -> None:
        super().__init__(**kwds)
        self._cb = cb
    
    def invoke(self, context: EvaluationContext) -> None:
        self._cb()

    @classmethod
    def make(cls, 
             what:InvocableOrSimpleCB, 
             **kwds:Unpack[InvocableSimpleCB.KWDS]
            ) -> 'Invocable':
        if isinstance(what, Invocable): return what
        if callable(what): return InvocableSimpleCB(what, **kwds)
        return Invocable.make(what)

class InvocableContextCB(NamedInvocable):
    """
    """
    def __init__(self, cb:Callable[[EvaluationContext], None],
                  **kwds:Unpack[NamedLocalIdentifiable.KWDS]
                ) -> None:
        super().__init__(**kwds)
        self._cb = cb
    
    def invoke(self, context: EvaluationContext) -> None:
        self._cb(context)

    @classmethod
    def make(cls, what:InvocableOrContextCB, **kwds:Unpack[InvocableContextCB.KWDS]) -> 'Invocable':
        if isinstance(what, Invocable): return what
        if callable(what): return InvocableContextCB(what, **kwds)
        return Invocable.make(what)

InvocableOrSimpleCB:TypeAlias = Union[Invocable, Callable[[], None]]
InvocableOrContextCB:TypeAlias = Union[Invocable, Callable[['EvaluationContext'], None]]

_sayInvocableImport.complete()

__all__ = [
    "Invocable",
    "InvocableSimpleCB",
    "InvocableContextCB",
    "InvocableOrSimpleCB",
    "InvocableOrContextCB",
]
