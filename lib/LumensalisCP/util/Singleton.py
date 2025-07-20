
from __future__ import annotations
try:
    from typing import Any
except ImportError:
    pass


class Singleton:
    """
    A simple singleton class that can be used to create singleton instances.
    """
    __byClass:dict[str,Singleton] = {}
    
    def __init__(self, name:str, i:Any  = None):
        self.__instance = None
        self.__name = name
        if i is not None:
            self.set(i)
    
    @property
    def name(self) -> str:
        """The name of the singleton instance."""
        return self.__name
    
    def get(self)->Any:
        assert self.__instance is not None
        return self.__instance
    
    def set(self, instance) -> None:
        # only set once
        assert self.__instance is None
        
        self.__instance = instance
        
        # make sure only one exists for this class
        cls = type(instance)
        assert self.__byClass.get(cls.__name__) is None
        self.__byClass[cls.__name__] = self
        
        
    def __call__(self): 
        """
        Allows the singleton to be called like a function to get the instance.
        """
        return self.get()        
