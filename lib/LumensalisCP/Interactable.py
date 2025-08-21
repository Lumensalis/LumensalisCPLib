from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__importProfile = getImportProfiler( __name__, globals() )

# pylint: disable=redefined-builtin,unused-variable,unused-argument,broad-exception-caught
# pyright: reportUnusedImport=false

from LumensalisCP.IOContext import *

from LumensalisCP.Main.Dependents import MainChild
from LumensalisCP.Triggers.Trigger import Trigger
from LumensalisCP.Eval.Evaluatable import NamedEvaluatableProtocolT, NamedEvaluatableProtocol


__importProfile.parsing()


#############################################################################
INTERACTABLE_ARG_T = TypeVar('INTERACTABLE_ARG_T')
INTERACTABLE_T = TypeVar('INTERACTABLE_T')

class INTERACTABLE_ARG_T_ADD_KWDS(TypedDict, Generic[INTERACTABLE_ARG_T,INTERACTABLE_T]):
    startingValue: NotRequired[INTERACTABLE_ARG_T]
    min: NotRequired[INTERACTABLE_ARG_T]
    max: NotRequired[INTERACTABLE_ARG_T]
    name: NotRequired[str]
    description: NotRequired[str]
    
class INTERACTABLE_ARG_T_KWDS(TypedDict, Generic[INTERACTABLE_ARG_T,INTERACTABLE_T]):
    startingValue: NotRequired[INTERACTABLE_ARG_T]
    min: NotRequired[INTERACTABLE_ARG_T]
    max: NotRequired[INTERACTABLE_ARG_T]
    name: NotRequired[str]
    description: NotRequired[str]
    kindMatch: NotRequired[type]
    kind: NotRequired[str|type]



INTERACTABLE_ARG_T_KWDST = GenericT(INTERACTABLE_ARG_T_KWDS)
#############################################################################

class Interactable( Generic[INTERACTABLE_ARG_T, INTERACTABLE_T]):
    
    def __init__(self,  
                 startingValue:INTERACTABLE_ARG_T,
                 min:Optional[INTERACTABLE_ARG_T] = None,
                 max:Optional[INTERACTABLE_ARG_T] = None,
                 description:str="",
                 kind:Optional[str|type]=None,
                 convertor:Optional[Callable[[INTERACTABLE_ARG_T|str],INTERACTABLE_T]]=None,
                 kindMatch: Optional[type]=None,
                 adjuster: Optional[Callable[[INTERACTABLE_T], INTERACTABLE_T]] = None
                 ) -> None:
        super().__init__()
        self.description = description or ""
        if kind is None:
            assert startingValue is not None
            kind = type(startingValue).__name__
        self.adjuster = adjuster
        self.kind = kind
        if kindMatch is not None:
            self.kindMatch = kindMatch
        elif isinstance(kind, type):
            self.kindMatch = kind
        elif isinstance( kind, str ): # pyright: ignore
            kType = globals().get(kind,None)
            if isinstance(kType,type):
                self.kindMatch = kType
            else:
                assert kType is None, f"kindMatch for {kind} is not a type: {kType}"

        kType = self.kindMatch        
        assert isinstance(kType, type ), f"kindMatch for {kind} is not a type: {kType}"
        assert kType is not type(None)
        assert kType is not type 

        if convertor is None:
            def convert(v:INTERACTABLE_ARG_T|str) -> INTERACTABLE_T:
                if isinstance(v,str):
                    v = eval(v)
                if isinstance(v, kType):
                    return v
                return kType(v)
            convertor = convert
        assert convertor is not None

        self.convertor:Callable[[INTERACTABLE_ARG_T|str],INTERACTABLE_T] = convertor

        self._min:INTERACTABLE_T|None = convertor(min) if min is not None else None
        self._max:INTERACTABLE_T|None = convertor(max) if max is not None else None
        self._interactValue:INTERACTABLE_T|None = None
        self._interactValue = convertor(startingValue) 

    def interactConvert( self, value: Any ) -> INTERACTABLE_T:
        if isinstance(value, str):
            try:
                value = self.convertor(value)
            except Exception as inst:
                print(f"failed converting {value} to {self.kind} : {inst}")
                raise
        
        if self.adjuster is not None:
            value = self.adjuster(value)

        if self._min is not None and value < self._min:
            value = self._min
        elif self._max is not None and value > self._max:
            value = self._max
        return value
        
        
InteractableT = GenericT(Interactable)

 
#############################################################################

__importProfile.complete()
