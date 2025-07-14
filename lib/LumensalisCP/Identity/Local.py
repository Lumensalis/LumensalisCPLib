from ..Debug import Debuggable
import LumensalisCP.pyCp.weakref as weakref
from ..CPTyping import ReferenceType, Optional

from LumensalisCP.pyCp.collections import UserList

class LocalIdentifiable(object):
    
    __nextId = 1
    
    @staticmethod
    def __getNextId( self2 ):
        # TODO : thread safe / groups
        id = LocalIdentifiable.__nextId
        LocalIdentifiable.__nextId += 1

    def __init__( self ):
        self.__localId = self.__getNextId(self)
        
    @property
    def localId(self): return self.__localId
    
    
class NamedLocalIdentifiable(LocalIdentifiable,Debuggable):
    
    def __init__( self, name:Optional[str] ):
        self.__name = name
        LocalIdentifiable.__init__(self)
        Debuggable.__init__(self)
        self.__nliContainerRef = name

    @property
    def name(self) -> str: return self.__name or self.nliDynamicName()
    
    @name.setter
    def name( self, name:str ):
        assert name is not None
        if self.__nliContainerRef is not None:
            c = self.__nliContainerRef()
            c.nliRenameChild( self, name )
        self.__name = name
        
    @property
    def __repr__(self):
        if self.__name is None:
            return self.nliDynamicName()
        return f"{self.__class__.__name__}({self.__name}:{self.localId})"

    #########################################################################
    
    __nliContainerRef:ReferenceType["NamedLocalIdentifiableContainerMixin"]
    __name:str
    
    def nliContainer(self) -> "NamedLocalIdentifiableContainerMixin"|None:
        c = self.__nliContainerRef
        return c if c is None else c()

    def setNlipContainer(self, container:"NamedLocalIdentifiableContainerMixin"):
        assert container is not None
        oldContainer = self.nliContainer
        if oldContainer is not None:
            oldContainer.nliRemoveChild(self)
        self.__nliContainerRef = weakref.ref( container )
        container.nliAddChild(self)

    @property
    def nliIsNamed(self) -> bool: return self.__name is not None
    

    def nliDynamicName(self) -> str:
        return self.__name or f"{self.__class__.__name__}:{id(self):X}"
    
    def nliContainers(self) -> list["NamedLocalIdentifiableContainerMixin"]|None:
        return None
        
#############################################################################

class NamedLocalIdentifiableContainerMixin( object ):
    
    def nliActualParent(self) -> NamedLocalIdentifiable: return self
    
    def nliRenameChild( self, child:NamedLocalIdentifiable, name:str ): pass
    
    def nliAddChild( self, child:NamedLocalIdentifiable ):
        raise NotImplemented
    
    def nliRemoveChild( self, child:NamedLocalIdentifiable ):
        raise NotImplemented
    
    
#############################################################################
    
class NamedLocalIdentifiableList(UserList, NamedLocalIdentifiableContainerMixin ):
    
    def __init__(self, items:Optional[list] = None, parent:Optional[NamedLocalIdentifiable]=None ):
        self.__parent = parent and weakref.ref(parent)
        super().__init__(items)

    def keys(self):
        return [v.name for v in self]

    def nliActualParent(self) -> NamedLocalIdentifiable:
        return self.__parent() if self.__parent is not None else self

    def nliAddChild( self, child:NamedLocalIdentifiable ):
        self.append( child )
    
    def nliRemoveChild( self, child:NamedLocalIdentifiable ):
        self.remove( child )
