from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__profileImport = getImportProfiler( "Identity.Local" )

# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

from LumensalisCP.common import *
from LumensalisCP.Debug import Debuggable
import LumensalisCP.pyCp.weakref as lcpWeakref
from LumensalisCP.CPTyping import ReferenceType, Optional, Iterable , Generic, TypeVar, GenericT
from LumensalisCP.pyCp.collections import GenericList, GenericListT

if TYPE_CHECKING:
    from .Proxy import GenericNamedLocalInstanceProxyAction
#############################################################################

__profileImport.parsing()

class LocalIdentifiable(CountedInstance):
    
    __nextId = 1
    __localId:int
    localsMap:ClassVar[dict[int,LocalIdentifiable]] = {}

    @staticmethod
    def __getNextId(  ): # pylint: disable=unused-argument
        # TODO : thread safe / groups 
        nextId = LocalIdentifiable.__nextId
        LocalIdentifiable.__nextId += 1
        return nextId

    def __init__( self ) -> None:
        super().__init__()
        localId = self.__getNextId()
        self.__localId = localId
        assert( LocalIdentifiable.localsMap.get(localId,None) is None ), f"localId {localId} already exists"
        LocalIdentifiable.localsMap[localId] = self

    @property
    def localId(self) -> int: return self.__localId

#############################################################################

class NliInterface(IDebuggable):
    def nliHasChildren(self) -> bool: ...
    def nliHasContainers(self) -> bool: ...
    def nliHasItems(self) -> bool: ...

    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]: ...

    def nliGetContainers(self) -> Iterable[NliContainerInterface]: ...

    def isContainer(self) -> bool: ...

#############################################################################
class NliContainerInterface(NliInterface):
    @property
    def containerName(self) -> str: ...


    def values(self) -> Iterable[Any]: ...

    def __getitem__(self, key:str|int) -> NamedLocalIdentifiable: ...
    
############################################################################# 
FULL_KWDS=TypeVar("FULL_KWDS")

class NamedLocalIdentifiable(LocalIdentifiable,NliInterface,Debuggable):

    _proxyActions:ClassVar[dict[str, dict[str,GenericNamedLocalInstanceProxyAction]]] = {}
    
    class KWDS(TypedDict):
        name:NotRequired[str]
        temporaryName:NotRequired[str]
    
    def __init__( self, 
                name:Optional[str]=None,
                temporaryName:Optional[str]=None
            ) -> None:
      
        self.__name = name
        self.__temporaryName = temporaryName

        LocalIdentifiable.__init__(self)
        Debuggable.__init__(self)

    @staticmethod 
    def extractInitArgs(kwds:FULL_KWDS) -> Tuple[FULL_KWDS,KWDS]:
        nliKwds:NamedLocalIdentifiable.KWDS = {
            'name': kwds.pop('name', None), # type: ignore
            'temporaryName': kwds.pop('temporaryName', None) # type: ignore
        }
        return kwds, nliKwds

    @property
    def name(self) -> str: return self.__name or self.__temporaryName or self.nliDynamicName()
    
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

    def isContainer(self) -> bool:
        return False

    #########################################################################

    #__nliContainerRef:ReferenceType["NliContainerMixin"]
    __nliContaining:list[ReferenceType[NliContainerInterface]]|None = None
    __name:str|None
    
    def nliGetContaining(self) -> Iterable[NliContainerInterface]|None:
        c = self.__nliContaining
        if c is None: return None
        for i in c:
            v = i()
            if v is not None: yield v

    
    def nliHasChildren(self) -> bool:
        return False
            
    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]:
        return tuple()


    def nliHasContainers(self) -> bool:
        return False
    
    def nliGetContainers(self) -> Iterable[NliContainerInterface]:
        return tuple()


    def nliHasItems(self) -> bool:
        return False


    def nliSetContainer(self, container:NliContainerMixin):
        assert container is not None
        #oldContainer = self.nliGetContaining()
        #if oldContainer is not None:
        #    oldContainer.nliRemoveChild(self)
        ensure( not container.nliContainsChild(self), "item %s already in %s", safeRepr(self), safeRepr(container) ) 
        assert isinstance(container, NliContainerInterface), "container must be a NliContainerInterface"        
        if self.__nliContaining is None:
            self.__nliContaining = [ lcpWeakref.lcpfRef( container ) ]
        else:
            self.__nliContaining.append( lcpWeakref.lcpfRef( container ) )
        container.nliAddChild(self)

    @property
    def nliIsNamed(self) -> bool: return self.__name is not None

    def nliDynamicName(self) -> str:
        if self.__name is not None: return self.__name
        cached = getattr(self, '_nliCachedName', None)
        if cached is None: 
            cached = f"{self.__class__.__name__}@{id(self):X}"
            self._nliCachedName = cached
        return cached

    def nliFind(self,name:str) -> NamedLocalIdentifiable|NliContainerInterface| None:
        containers = self.nliGetContainers() # pylint: disable=assignment-from-none
        for container in containers:
            if container.containerName == name:
                return container
            
        children = self.nliGetChildren() # pylint: disable=assignment-from-none
        for child in children:
            if child.name == name:
                return child
        return None

    
#############################################################################


class NliContainerMixin( NliContainerInterface ):
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
    
    def isContainer(self) -> bool:
        return True

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

    def nliHasItems(self) -> bool:
        return len(self.data) > 0

    def iter(self) -> Iterable[_NLIListT]:
        return iter(self.data)
    
    def keys(self) -> list[str]:
        return [v.name for v in self.data] # type: ignore[return-value]

    def __len__(self) -> int:
        return len(self.data)
    
    def isContainer(self) -> bool:
        return True
    

    
    @property
    def containerName(self) -> str: return self.name

    def values(self) -> list[_NLIListT]:
        return self.data

    def get(self, key:str, default:Optional[_NLIListT]=None) -> _NLIListT:
        for v in self.data:
            if v.name == key:
                return v
        assert default is not None, "default must be provided if key not found"
        return default

    def nliContainsChild( self, child:NamedLocalIdentifiable ) -> bool:
        for v in self.data:
            if v is child: return True
        return False

    def nliContains( self, name:str ) -> bool:
        for v in self.data:
            if v.name == name: return True
        return False
    
    def append( self, item:_NLIListT ) -> None:
        assert isinstance(item, NamedLocalIdentifiable), "item must be a NamedLocalIdentifiable"
        if self.enableDbgOut: self.dbgOut( "append( %r )", item )
        item.nliSetContainer(self)


    def nliAddChild( self, child:_NLIListT ) -> None: # type:ignore[override]
        self.data.append( child )
    
    def nliRemoveChild( self, child:_NLIListT ) -> None: # type:ignore[override]
        self.data.remove( child )

    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]:
        return tuple()
            
    def nliFind(self,name:str) -> NamedLocalIdentifiable|None:
        for child in self.data:
            if child.name == name:
                return child
        return None

#############################################################################


__all__ = ['LocalIdentifiable',
           'NamedLocalIdentifiable',
           'NamedLocalIdentifiableWithParent',
            'NliContainerMixin','NliList', 'NliInterface']

__profileImport.complete(globals())
