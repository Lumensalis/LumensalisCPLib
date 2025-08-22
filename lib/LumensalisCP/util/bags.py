

from LumensalisCP.CPTyping import Iterable, Any, Iterator, Generic, TypeVar

class Bag(object): # type: ignore

    def __init__(self, *args:Any, **kwargs:Any) -> None:
        if len(args) > 0:
            assert len(args) == 1, "Bag can only be initialized with a single argument"
            assert len(kwargs) == 0, "Bag can only be initialized with a single argument"
            for key, value in args[0].items():
                setattr(self, key, value)
        elif len(kwargs) > 0:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __getitem__(self, name:str) ->Any:
        try:
            return getattr(self, name)
        except AttributeError:
            raise KeyError(name)

    def __setitem__(self, name:str, value:Any):
        setattr(self, name, value)

#############################################################################

_NLT = TypeVar("_NLT" )
class NamedList(Generic[_NLT]):
    def __init__(self ) -> None:
        self.__items: list[_NLT] = []
        self.__byName: dict[str, _NLT] = {}
        
    def __iter__(self) -> Iterator[_NLT]:
        return iter(self.__items)

    def __len__(self) -> int:
        return len(self.__items)
    
    def keys(self) -> Iterable[str]:
        return self.__byName.keys()
    
    def values(self) -> Iterable[_NLT]:
        return self.__byName.values()

    def items(self) -> Iterable[tuple[str,_NLT]]:
        return self.__byName.items()
    
    def __getitem__(self, x:int|str) -> _NLT:
        if isinstance(x, str):
            return self.__byName[x]
        return self.__items[x]

    def append( self, item:_NLT ) -> None:
        name = getattr(item,'name',None)
        if name is not None:
            assert item.name not in self.__byName
            self.__byName[name] = item
        self.__items.append(item)
                
    def extend( self, iterable:Iterable[_NLT] ):
        for item in iterable:
            self.append(item)

    def __getattr__(self, name:str) -> _NLT:
        try:
            return self.__byName[name]
        except Exception as inst:
            raise AttributeError(f"NamedList has no item named {name!r}") from inst

#############################################################################
