from __future__ import annotations

from typing import TypeVar, Generic
from LumensalisCP.common import *
from LumensalisCP.Debug import Debuggable
import LumensalisCP.pyCp.weakref as lcpWeakref
from LumensalisCP.CPTyping import ReferenceType, Optional, Iterable

# pylint: disable=unused-argument, super-init-not-called, unused-private-member

from LumensalisCP.pyCp.collections import UserList

class LocalIdentifiable(object):
    
    def __init__( self ): ...
        
    @property
    def localId(self) -> int: ...
    
    


class NamedLocalIdentifiableInterface:
    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]|None: ...

    def nliGetContainers(self) -> Iterable[NamedLocalIdentifiableContainerMixin]|None: ...
    #@overload
    def nliSetContainer(self, container:NamedLocalIdentifiableContainerMixin[Self]): ...
    
    #def nliSetContainer(self, container:NamedLocalIdentifiableContainerMixin): ...

_NLIT_co = TypeVar('_NLIT_co',
                   covariant=True, 
                   #contravariant=False,
                   bound=NamedLocalIdentifiableInterface)
            
class NamedLocalIdentifiable(LocalIdentifiable,NamedLocalIdentifiableInterface,Debuggable): 
    
    def __init__( self, name:Optional[str]=None ): ...

    @property
    def name(self) -> str: ...
    
    @name.setter
    def name( self, name:str ): ...

    #########################################################################

    __nliContaining:list[ReferenceType[NamedLocalIdentifiableContainerMixin[Self]]]|None 
    __name:str|None
    
    def nliGetContaining(self) -> Iterable[NamedLocalIdentifiableContainerMixin[Self]]|None: ...
        
    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]|None: ...

    def nliGetContainers(self) -> Iterable[NamedLocalIdentifiableContainerMixin]|None: ...

    def nliSetContainer(self, container:NamedLocalIdentifiableContainerMixin[Self]): ...

    @property
    def nliIsNamed(self) -> bool: ...

    def nliDynamicName(self) -> str: ...
        
    def nliFind(self,name:str) -> NamedLocalIdentifiable|NamedLocalIdentifiableContainerMixin| None: ...
        
    
#############################################################################

class NamedLocalIdentifiableContainerMixin[_NLIT_co]( NamedLocalIdentifiableInterface ):
    @property
    def containerName(self) -> str: ...
    @property
    def name(self) -> str: ...
    
    def nliRenameChild( self, child:_NLIT_co, name:str ): ...
    def nliAddChild( self, child:_NLIT_co ) -> None: ...
    def nliRemoveChild( self, child:_NLIT_co ) -> None: ...
    def nliContainsChild( self, child:_NLIT_co ) -> bool: ...

    
#############################################################################
    
class NamedLocalIdentifiableWithParent( NamedLocalIdentifiable ):
    __parent:lcpWeakref.ReferenceType[NamedLocalIdentifiable]|None
    
    def __init__(self, name:Optional[str] = None, parent:Optional[NamedLocalIdentifiable]=None ): ...
    
    def nliGetActualParent(self) -> NamedLocalIdentifiable|None: ...

#############################################################################

    
class NamedLocalIdentifiableList[T](NamedLocalIdentifiableWithParent, UserList, NamedLocalIdentifiableContainerMixin[T] ):
    
    def __init__(self, name:Optional[str] = None, items:Optional[list[T]] = None, parent:Optional[NamedLocalIdentifiable]=None ): ...

    def keys(self) -> Iterable[str]: ...

    @property
    def containerName(self) -> str: ...
    
    def values(self) -> Iterable[T]: ...

    def get(self, key:str, default:Optional[T]=None) -> T|None: ...

    def nliContainsChild( self, child:T ) -> bool: ...
    def nliAddChild( self, child:T ): ...
    def nliRemoveChild( self, child:T ): ...
    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]|None: ...
    def nliFind(self,name:str) -> NamedLocalIdentifiable|None: ...

__all__ = ['LocalIdentifiable','NamedLocalIdentifiable','NamedLocalIdentifiableWithParent',
            'NamedLocalIdentifiableContainerMixin','NamedLocalIdentifiableList', 'NamedLocalIdentifiableInterface']
