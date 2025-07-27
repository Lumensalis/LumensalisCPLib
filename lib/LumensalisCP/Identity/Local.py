from __future__ import annotations

from LumensalisCP.Main.PreMainConfig import ImportProfiler
_sayIdentityLocalImport = ImportProfiler( "Identity.Local" )

from LumensalisCP.common import *
from LumensalisCP.Debug import Debuggable
import LumensalisCP.pyCp.weakref as lcpWeakref
from LumensalisCP.CPTyping import ReferenceType, Optional, Iterable , Generic, TypeVar, GenericT
from LumensalisCP.pyCp.collections import GenericList, GenericListT

_sayIdentityLocalImport.parsing()

class LocalIdentifiable(object):
    
    __nextId = 1
    __localId:int

    @staticmethod
    def __getNextId(  ): # pylint: disable=unused-argument
        # TODO : thread safe / groups 
        nextId = LocalIdentifiable.__nextId
        LocalIdentifiable.__nextId += 1
        return nextId

    def __init__( self ) -> None:
        self.__localId = self.__getNextId()
        
    @property
    def localId(self) -> int: return self.__localId
    
#############################################################################    
    
class NliInterface:
    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]|None: ...

    def nliGetContainers(self) -> Iterable[NliContainerBaseMixin]|None: ...
    

#############################################################################    
class NliContainerBaseMixin(NliInterface):
    @property
    def containerName(self) -> str: ...
    @property
    def name(self) -> str: ...

    def __getitem__(self, key:str|int) -> NamedLocalIdentifiable: ...
    
############################################################################# 

                    
                    
class NamedLocalIdentifiable(LocalIdentifiable,NliInterface,Debuggable):

    class KWDS(TypedDict):
        name:NotRequired[str]
    
    def __init__( self, name:Optional[str]=None ):
        self.__name = name
        LocalIdentifiable.__init__(self)
        Debuggable.__init__(self)

    @property
    def name(self) -> str: return self.__name or self.nliDynamicName()
    
    @name.setter
    def name( self, name:str ):
        assert name is not None
        containing = getattr(self,'__containing',None)
        if containing is not None:
            for containerRef in containing:
                containerRef().nliRenameChild( self, name )
        self.__name = name

    def __repr__(self):
        if self.__name is None:
            return self.nliDynamicName()
        return f"{self.__class__.__name__}({self.__name}@{self.localId})"

    #########################################################################

    #__nliContainerRef:ReferenceType["NliContainerMixin"]
    __nliContaining:list[ReferenceType[NliContainerBaseMixin]]|None = None
    __name:str|None
    
    def nliGetContaining(self) -> Iterable[NliContainerBaseMixin]|None:
        c = self.__nliContaining
        if c is None: return None
        for i in c:
            v = i()
            if v is not None: yield v
        
    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]|None:
        return None

    def nliGetContainers(self) -> Iterable[NliContainerBaseMixin]|None:
        return None

    def nliSetContainer(self, container:NliContainerMixin):
        assert container is not None
        #oldContainer = self.nliGetContaining()
        #if oldContainer is not None:
        #    oldContainer.nliRemoveChild(self)
        ensure( not container.nliContainsChild(self), "item %s already in %s", safeRepr(self), safeRepr(container) ) 
        assert isinstance(container, NliContainerBaseMixin), "container must be a NliContainerBaseMixin"        
        if self.__nliContaining is None:
            self.__nliContaining = [ lcpWeakref.lcpfRef( container ) ]
        else:
            self.__nliContaining.append( lcpWeakref.lcpfRef( container ) )
        container.nliAddChild(self)

    @property
    def nliIsNamed(self) -> bool: return self.__name is not None

    def nliDynamicName(self) -> str:
        return self.__name or f"{self.__class__.__name__}@{id(self):X}"

    def nliFind(self,name:str) -> NamedLocalIdentifiable|NliContainerBaseMixin| None:
        containers = self.nliGetContainers() # pylint: disable=assignment-from-none
        if containers is not None:
            for container in containers:
                if container.containerName == name:
                    return container
                
        children = self.nliGetChildren() # pylint: disable=assignment-from-none
        if children is not None:
            for child in children:
                if child.name == name:
                    return child
        return None

    
#############################################################################


class NliContainerMixin( NliContainerBaseMixin ):
    @property
    def containerName(self) -> str: ...
    @property
    def name(self) -> str: ...
    
    def nliRenameChild( self, child:NamedLocalIdentifiable, name:str ): pass
    
    def nliAddChild( self, child:NamedLocalIdentifiable ) -> None:
        raise NotImplementedError
    
    def nliRemoveChild( self, child:NamedLocalIdentifiable ) -> None:
        raise NotImplementedError
    
    def nliContainsChild( self, child:NamedLocalIdentifiable ) -> bool:
        raise NotImplementedError

#############################################################################
    
class NamedLocalIdentifiableWithParent( NamedLocalIdentifiable ):
    __parent:lcpWeakref.ReferenceType[NamedLocalIdentifiable]|None
    
    def __init__(self, name:Optional[str] = None, parent:Optional[NamedLocalIdentifiable]=None ):
        NamedLocalIdentifiable.__init__(self,name=name)
        self.__parent = parent if parent is None else lcpWeakref.lcpfRef(parent)
    
    def nliGetActualParent(self) -> NamedLocalIdentifiable|None: 
        if self.__parent is None: return None
        return self.__parent() 

#############################################################################
_NLIListT = TypeVar('_NLIListT', bound='NamedLocalIdentifiable')    
class NliList(NamedLocalIdentifiableWithParent, GenericListT[_NLIListT], NliContainerMixin ):
    
    def __init__(self, name:Optional[str] = None, items:Optional[list[NamedLocalIdentifiable]] = None, parent:Optional[NamedLocalIdentifiable]=None ):
        #self.__parent = parent and lcpWeakref.ref(parent)
        NamedLocalIdentifiableWithParent.__init__(self,name=name,parent=parent)
        GenericList.__init__(self,items) # type: ignore

    
    def __iter__(self) -> Iterable[_NLIListT]:
        return iter(self.data)
    
    def __next__(self) -> Generator[_NLIListT]:
        for item in self.data:
            yield item

    def iter(self) -> Iterable[_NLIListT]:
        return iter(self.data)
    
    def keys(self) -> list[str]:
        return [v.name for v in self] # type: ignore[return-value]
    
    @property
    def containerName(self): return self.name

    

    def values(self) -> list[_NLIListT]:
        return self.data

    def get(self, key:str, default:Optional[_NLIListT]=None) -> _NLIListT:
        for v in self:
            if v.name == key:
                return v
        assert default is not None, "default must be provided if key not found"
        return default

    def nliContainsChild( self, child:NamedLocalIdentifiable ) -> bool:
        for v in self.data:
            if v is child: return True
        return False

    
    def nliAddChild( self, child:_NLIListT ):
        self.append( child )
    
    def nliRemoveChild( self, child:_NLIListT ):
        self.remove( child )

    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]|None:
        return None
            
    def nliFind(self,name:str) -> NamedLocalIdentifiable|None:
        for child in self:
            if child.name == name:
                return child
        return None

_sayIdentityLocalImport.complete()

__all__ = ['LocalIdentifiable',
           'NamedLocalIdentifiable',
           'NamedLocalIdentifiableWithParent',
            'NliContainerMixin','NliList', 'NliInterface']
