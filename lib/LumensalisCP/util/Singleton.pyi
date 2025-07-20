
from __future__ import annotations
from typing import Any, Optional, Generic, TypeVar

# pylint: disable=unused-argument

T = TypeVar('T')

class Singleton(Generic[T]):
    """
    A simple singleton class that can be used to create singleton instances.
    """
    
    def __init__(self, name:str, i:T|None  = None): ... 
        
    def get(self)->T:...
    
    def set(self, instance:T) -> None: ...

    def __call__(self) -> T: ...
