from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__importProfile = getImportProfiler( __name__, globals() )

# pylint: disable=redefined-builtin,unused-variable,unused-argument,broad-exception-caught
# pyright: reportUnusedImport=false

from LumensalisCP.common  import *
from LumensalisCP.Interactable.InteractableKWDS import *

__importProfile.parsing()

#############################################################################

#############################################################################

class Interactable( Generic[INTERACTABLE_T]):
    
    def __init__(self,  
                 startingValue:Optional[INTERACTABLE_T] = None,
                 min:Optional[INTERACTABLE_T] = None,
                 max:Optional[INTERACTABLE_T] = None,
                 description:str="",
                 kind:Optional[str|type]=None,
                 convertor:Optional[Callable[[INTERACTABLE_T|str],INTERACTABLE_T]]=None,
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
            def convert(v:INTERACTABLE_T|str) -> INTERACTABLE_T:
                if isinstance(v,str):
                    v = eval(v)
                if isinstance(v, kType):
                    return v # type: ignore
                return kType(v)
            convertor = convert
        assert convertor is not None

        self.convertor:Callable[[INTERACTABLE_T|str],INTERACTABLE_T] = convertor

        self._min:INTERACTABLE_T|None = convertor(min) if min is not None else None
        self._max:INTERACTABLE_T|None = convertor(max) if max is not None else None
        self.startingValue = startingValue
        self._interactValue:INTERACTABLE_T|None = None

        self._interactValue = convertor(startingValue)  # type: ignore

    def interactSpec(self) -> dict[str, Any]:
        return {
            "name": getattr(self, "name", None),
            "description": self.description,
            "kind": str(self.kind),
            "kindMatch": str(self.kindMatch),
            "startingValue": self.startingValue,
            "min": self._min,
            "max": self._max,
        }

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

__all__ = [
    "Interactable","InteractableT",
    "INTERACTABLE_ARG_T",
    "INTERACTABLE_T",
    "INTERACTABLE_KWDS",
    "INTERACTABLE_ARG_T_ADD_KWDS"
]

__importProfile.complete()
