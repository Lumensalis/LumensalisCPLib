from __future__ import annotations

#############################################################################

from LumensalisCP.ImportProfiler import  getImportProfiler
__profileImport = getImportProfiler( __name__, globals() )

#############################################################################

from LumensalisCP.CPTyping import *
from LumensalisCP.common import safeFmt

__profileImport.parsing()

TIN =  TypeVar('TIN' ) #, bound=AnyRGBValue)
T_TARGET = TypeVar('T_TARGET' ) #, bound='RGB') 

SetterFunction:TypeAlias = Callable[[TIN, T_TARGET], None]

class Setter(Generic[TIN,T_TARGET]):
    #def __init__(self, setters:Optional[dict[type|str, Callable[[TIN], T_TARGET]]]=None) -> None:
    
    def __init__(self) -> None:
        self._setters:dict[type|str, Callable[[TIN, T_TARGET],None]] = {}
        self._classSetters: list[ tuple[ type, Callable[[TIN, T_TARGET],None]] ] = []

    def registerSetter( self, _type:type, cf:Callable[[TIN, T_TARGET],None]) -> None:
        self._setters[_type] = cf
        self._setters[_type.__name__] = cf
        if _type not in { int, bool, float, str, list, tuple, type(None)}:
            self._classSetters.append( (_type, cf) )

    def supportsType( self, _type:type ) -> bool:
        return _type in self._setters or _type.__name__ in self._setters
    
    def __call__(self, value:TIN, target:T_TARGET) -> None: 
        Setter = self._setters.get(type(value),None)
        if Setter is not None:
            return Setter(value, target)
        for _type, Setter in self._classSetters:
            if isinstance(value, _type):
                return Setter(value,target)
        assert False, safeFmt( "cannot set %r (%s)", value, type(value))


    def defineRegisterSetter( self, _type:type ) -> Callable[..., None]:
        def register( callback: Callable[[Any,T_TARGET],None] ) -> None:
            self.registerSetter(_type, callback)
            
        return register


__profileImport.complete(globals())    