from __future__ import annotations

#############################################################################

from LumensalisCP.ImportProfiler import  getImportProfiler
__sayUtilConvertorImport = getImportProfiler( globals() ) # "util.Convertor"

#from LumensalisCP.CPTyping import TypeAlias, ZeroToOne,Union, Type, Callable, Optional,  Any, Tuple, NewType, ClassVar
#from LumensalisCP.CPTyping import Generic, TypeVar

from LumensalisCP.CPTyping import *
from LumensalisCP.common import safeFmt
TIN =  TypeVar('TIN' ) #, bound=AnyRGBValue)
TOUT = TypeVar('TOUT' ) #, bound='RGB') 

class Convertor(Generic[TIN,TOUT]):
    #def __init__(self, convertors:Optional[dict[type|str, Callable[[TIN], TOUT]]]=None) -> None:
    
    def __init__(self) -> None:
        self._convertors:dict[type|str, Callable[[TIN], TOUT]] = {}
        self._classConvertors: list[ tuple[ type, Callable[[TIN], TOUT] ] ] = []

    def registerConvertor( self, _type:type, cf:Callable[[TIN],TOUT]) -> None:
        self._convertors[_type] = cf
        self._convertors[_type.__name__] = cf
        if _type not in { int, bool, float, str, list, tuple, type(None)}:
            self._classConvertors.append( (_type, cf) )

    def supportsType( self, _type:type ) -> bool:
        return _type in self._convertors or _type.__name__ in self._convertors
    
    def __call__(self, value:TIN) -> TOUT: 
        convertor = self._convertors.get(type(value),None)
        if convertor is not None:
            return convertor(value)
        for _type, convertor in self._classConvertors:
            if isinstance(value, _type):
                return convertor(value)
        assert False, safeFmt( "cannot convert %r (%s)", value, type(value))


    def defineRegisterConvertor( self, _type:type ):
        def register( callback: Callable[[Any],TOUT] ):
            self.registerConvertor(_type, callback)
            return None
        return register

    def registerChildClass(self) -> Callable[[type], type]:
        def r( cls:type ) -> Type[Any]:
            self.registerConvertor(cls, lambda v: cls(v))
            return cls
        return r

__sayUtilConvertorImport.complete(globals())    