from typing import Iterable, Iterator, Any, Sequence

class Bag(dict):
    
    def __getattr__(self, name):
        try:
            return self[name]
        except:
            return super().__getattribute__(name)
        
    def __setattr__(self, name, value):
        self[name] = value
        
#############################################################################
        
class NamedList[T](object):
    __items = []
    __byName = {}
        
    def __init__(self ): ...
        
    def __iter__(self) -> Iterator[T]: ...
    def __len__(self) -> int: ...
    
    def keys(self) -> Sequence[str]: ...
    
    def values(self)-> Sequence[T]: ...

    def items(self) -> Sequence[tuple[str,T]]: ...
    
    def __getitem__(self, x) -> T: ...

    def append( self, item:T ): ...
                
    def extend( self, iterable:Iterable[T] ): ...

    def __getattr__(self, name:str)-> T: ...
