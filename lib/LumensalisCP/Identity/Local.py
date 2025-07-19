from __future__ import annotations
from LumensalisCP.common import *
from LumensalisCP.Debug import Debuggable
import LumensalisCP.pyCp.weakref as lcpWeakref
from LumensalisCP.CPTyping import ReferenceType, Optional, Iterable

from LumensalisCP.pyCp.collections import UserList

class LocalIdentifiable(object):
    
    __nextId = 1
    
    @staticmethod
    def __getNextId( self2 ):
        # TODO : thread safe / groups
        id = LocalIdentifiable.__nextId
        LocalIdentifiable.__nextId += 1
        return id

    def __init__( self ):
        self.__localId = self.__getNextId(self)
        
    @property
    def localId(self): return self.__localId
    
    
class NamedLocalIdentifiableInterface:
    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]|None: ...

    def nliGetContainers(self) -> Iterable[NamedLocalIdentifiableContainerMixin]|None: ...
    def nliSetContainer(self, container:NamedLocalIdentifiableContainerMixin): ...
            
class NamedLocalIdentifiable(LocalIdentifiable,NamedLocalIdentifiableInterface,Debuggable):
    
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

    #__nliContainerRef:ReferenceType["NamedLocalIdentifiableContainerMixin"]
    __nliContaining:list[ReferenceType['NamedLocalIdentifiableContainerMixin']]|None = None
    __name:str|None
    
    def nliGetContaining(self) -> Iterable["NamedLocalIdentifiableContainerMixin"]|None:
        c = self.__nliContaining
        if c is None: return None
        for i in c:
            v = i()
            if v is not None: yield v
        
    def nliGetChildren(self) -> Iterable['NamedLocalIdentifiable']|None:
        return None

    def nliGetContainers(self) -> Iterable["NamedLocalIdentifiableContainerMixin"]|None:
        return None

    def nliSetContainer(self, container:"NamedLocalIdentifiableContainerMixin"):
        assert container is not None
        #oldContainer = self.nliGetContaining()
        #if oldContainer is not None:
        #    oldContainer.nliRemoveChild(self)
        ensure( not container.nliContainsChild(self), "item %s already in %s", safeRepr(self), safeRepr(container) ) 
        if self.__nliContaining is None:
            self.__nliContaining = [ lcpWeakref.lcpfRef( container ) ]
        else:
            self.__nliContaining.append( lcpWeakref.lcpfRef( container ) )
        container.nliAddChild(self)

    @property
    def nliIsNamed(self) -> bool: return self.__name is not None

    def nliDynamicName(self) -> str:
        return self.__name or f"{self.__class__.__name__}@{id(self):X}"

    def nliFind(self,name:str) -> "NamedLocalIdentifiable|NamedLocalIdentifiableContainerMixin| None":
        containers = self.nliGetContainers()
        if containers is not None:
            for container in containers:
                if container.containerName == name:
                    return container
                
        children = self.nliGetChildren()
        if children is not None:
            for child in children:
                if child.name == name:
                    return child
        return None

    
#############################################################################

class NamedLocalIdentifiableContainerMixin( NamedLocalIdentifiableInterface ):
    @property
    def containerName(self) -> str: ...
    @property
    def name(self) -> str: ...
    
    def nliRenameChild( self, child:NamedLocalIdentifiable, name:str ): pass
    
    def nliAddChild( self, child:NamedLocalIdentifiable ) -> None:
        raise NotImplemented
    
    def nliRemoveChild( self, child:NamedLocalIdentifiable ) -> None:
        raise NotImplemented
    
    def nliContainsChild( self, child:NamedLocalIdentifiable ) -> bool:
        raise NotImplemented
    
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
    
class NamedLocalIdentifiableList(NamedLocalIdentifiableWithParent, UserList, NamedLocalIdentifiableContainerMixin ):
    
    def __init__(self, name:Optional[str] = None, items:Optional[list] = None, parent:Optional[NamedLocalIdentifiable]=None ):
        #self.__parent = parent and lcpWeakref.ref(parent)
        NamedLocalIdentifiableWithParent.__init__(self,name=name,parent=parent)
        UserList.__init__(self,items)

    def keys(self):
        return [v.name for v in self]
    @property
    def containerName(self): return self.name
    
    def values(self):
        return self.data

    def get(self, key:str, default:Optional[Any]=None):
        for v in self:
            if v.name == key:
                return v
        return default

    def nliContainsChild( self, child:NamedLocalIdentifiable ) -> bool:
        for v in self.data:
            if v is child: return True
        return False

    
    def nliAddChild( self, child:NamedLocalIdentifiable ):
        self.append( child )
    
    def nliRemoveChild( self, child:NamedLocalIdentifiable ):
        self.remove( child )

    def nliGetChildren(self) -> Iterable['NamedLocalIdentifiable']|None:
        return self
            
    def nliFind(self,name:str) -> "NamedLocalIdentifiable|None":
        for child in self:
            if child.name == name:
                return child
        return None

__all__ = ['LocalIdentifiable','NamedLocalIdentifiable','NamedLocalIdentifiableWithParent',
            'NamedLocalIdentifiableContainerMixin','NamedLocalIdentifiableList', 'NamedLocalIdentifiableInterface']