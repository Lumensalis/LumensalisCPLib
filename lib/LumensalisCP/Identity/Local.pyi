from __future__ import annotations

from LumensalisCP.common import *
from LumensalisCP.Debug import Debuggable
import LumensalisCP.pyCp.weakref as lcpWeakref
from LumensalisCP.CPTyping import ReferenceType, Optional, Iterable, TypeVar

# pylint: disable=unused-argument, super-init-not-called, unused-private-member

from LumensalisCP.pyCp.collections import GenericList

class LocalIdentifiable(object):
    
    def __init__( self ) -> None: ...
        
    @property
    def localId(self) -> int: ...

class NliInterface( Protocol):
    @property
    def name(self) -> str: ...
    
    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]: ...

    def nliGetContainers(self) -> Iterable[NliContainerInterface]: ...

#############################################################################    
class NliContainerInterface( NliInterface ):
    @property
    def containerName(self) -> str: ...


    def __getitem__(self, key:str|int) -> NamedLocalIdentifiable: ...
    #def nliSetContainer(self, container:NliContainerMixin): ...

#############################################################################    

class NamedLocalIdentifiable(LocalIdentifiable,NliInterface,Debuggable): 
    
    class KWDS(TypedDict):
        name:NotRequired[str]
        temporaryName:NotRequired[str]
    
    def __init__( self, 
                name:Optional[str]=None,
                temporaryName:Optional[str]=None
            ) -> None: ...

    @staticmethod 
    def extractInitArgs(kwds:dict[str,Any]|Any) -> dict[str,Any]: ...
        
    @property
    def name(self) -> str: ...
    
    @name.setter
    def name( self, name:str ) -> None: ...

    #########################################################################

    __nliContaining:list[ReferenceType[NliContainerInterface]]|None 
    __name:str|None
    
    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]: ...
        
    def nliGetContainers(self) -> Iterable[NliContainerInterface]: ...

    def nliGetContaining(self) -> Iterable[NliContainerInterface]: ...

    def nliSetContainer(self, container:NliContainerMixin[Self]) -> None: ...

    @property
    def nliIsNamed(self) -> bool: ...

    def nliDynamicName(self) -> str: ...
        
    def nliFind(self,name:str) -> NamedLocalIdentifiable|NliContainerInterface| None: ...
        
    
#############################################################################

_NLIT_co = TypeVar('_NLIT_co',
                   covariant=True, 
                   #contravariant=False,
                   bound=NliInterface)

#class NliContainerMixin[_NLIT_co=NamedLocalIdentifiable]( NliInterface ,NliContainerInterface):

class NliContainerMixin[_NLIT_co]( NliContainerInterface):
    @property
    def containerName(self) -> str: ...
    @property
    def name(self) -> str: ...

    def nliRenameChild( self, child:_NLIT_co, name:str ) -> None: ...
    def nliAddChild( self, child:_NLIT_co ) -> None: ...
    def nliRemoveChild( self, child:_NLIT_co ) -> None: ...
    def nliContainsChild( self, child:_NLIT_co ) -> bool: ...

    
#############################################################################
    
class NamedLocalIdentifiableWithParent( NamedLocalIdentifiable ):
    __parent:lcpWeakref.ReferenceType[NamedLocalIdentifiable]|None
    
    def __init__(self, name:Optional[str] = None, parent:Optional[NamedLocalIdentifiable]=None ) -> None: ...

    def nliGetActualParent(self) -> NamedLocalIdentifiable|None: ...

#############################################################################

    
class NliList[T](NamedLocalIdentifiableWithParent, GenericList[T], NliContainerMixin[T] ):
    
    def __init__(self, name:Optional[str] = None, items:Optional[list[T]] = None, parent:Optional[NamedLocalIdentifiable]=None ) -> None: ...

    def keys(self) -> Iterable[str]: ...

    @property
    def containerName(self) -> str: ...
    
    def values(self) -> Iterable[T]: ...

    def get(self, key:str, default:Optional[T]=None) -> T|None: ...

    def nliContainsChild( self, child:T ) -> bool: ...
    def nliAddChild( self, child:T ) -> None: ...
    def nliRemoveChild( self, child:T ) -> None: ...
    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]: ...
    def nliFind(self,name:str) -> NamedLocalIdentifiable|None: ...

__all__ = ['LocalIdentifiable','NamedLocalIdentifiable','NamedLocalIdentifiableWithParent',
            'NliContainerMixin','NliList', 'NliInterface','NliContainerInterface']
