from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( __name__, globals() )

# pyright: reportPrivateUsage=false,reportUnusedImport=false

from LumensalisCP.Temporal.Refreshable import Refreshable, \
    RefreshableListInterface, RfMxnActivatable, RfMxnPeriodic

from LumensalisCP.Temporal import RefreshableListRL

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.util.Reloadable import ReloadableClass, reloadingMethod


if TYPE_CHECKING:
    from  LumensalisCP.Eval.Expressions import EvaluationContext

#############################################################################

@ReloadableClass([RefreshableListRL])
class RefreshableListImplementation(RefreshableListInterface ):

    class KWDS(TypedDict):
        pass

    def __init__(self, **kwds:Unpack[KWDS]) -> None:
        super().__init__()#**kwds)
        self._dirtyCount = 0
        self._sortCount = 0
        self.__processCount = 0
        self.__extraCount = 0
        self._refreshables:list[Refreshable] = []
        self._nextListRefresh:TimeInSeconds|None = None

    def __len__(self) -> int:
        return len(self._refreshables)
    
    def __iter__(self) -> Iterator[Refreshable]:
        return iter(self._refreshables)
    
    @reloadingMethod
    def __processOne( self, context:EvaluationContext, when:TimeInSeconds, item:Refreshable, index:int ) -> None:  ...
    

    def __assertSorted(self) -> None:
        refreshForSortedTest = 0
        for item in self._refreshables:
            assert item.nextRefresh is not None
            assert item.nextRefresh >=  refreshForSortedTest
            refreshForSortedTest = item.nextRefresh

    def processFinishedDirty( self, context:EvaluationContext ) -> None:
        if self.enableDbgOut: self.dbgOut( "processFinishedDirty, dirtyCount = %d", self._dirtyCount )

    @property
    def processCount(self) -> int:
        return self.__processCount

    @reloadingMethod
    def process( self, context:EvaluationContext, when:TimeInSeconds ) -> None: ...

    def addActive( self, context:EvaluationContext, item:Refreshable, 
                  nextRefresh:Optional[TimeInSeconds]=None ) -> None: ...

    def add( self, context:EvaluationContext, item:Refreshable, nextRefresh:Optional[TimeInSeconds]=None ) -> None: ...
    
    def _setNextListRefreshChanged(self,context:EvaluationContext,nextRefresh:Optional[TimeInSeconds]=None) -> None: ...

    def remove( self,  context:EvaluationContext, item:Refreshable ) -> None: ...

    def nextRefreshChanged( self, context:EvaluationContext, item:Refreshable ) -> None: ...

    def getNextRefreshForList(self, context:EvaluationContext, when:TimeInSeconds) -> TimeInSeconds|None: ...

    def markDirty( self, context:EvaluationContext, item:Refreshable|None ) -> None: ...

    def _sort(self, context:EvaluationContext, when:TimeInSeconds) -> None: ...

#############################################################################

class RootRefreshableList(RefreshableListImplementation, NamedLocalIdentifiable):

    class KWDS(NamedLocalIdentifiable.KWDS, RefreshableListImplementation.KWDS):
        pass

    def __init__(self, **kwds:Unpack[KWDS]) -> None:
        nliKwds = NamedLocalIdentifiable.extractInitArgs(kwds)
        RefreshableListImplementation.__init__(self, **kwds)
        NamedLocalIdentifiable.__init__(self, **nliKwds)


#############################################################################

class NestedRefreshableList(RefreshableListImplementation,
                RfMxnActivatable, 
                Refreshable ):
    
    RFD_autoRefresh:ClassVar[bool] = True

    class KWDS(Refreshable.KWDS, RefreshableListImplementation.KWDS,
               RfMxnActivatable.KWDS):
        pass

    def __init__(self, parent:RefreshableListInterface, **kwds:Unpack[KWDS] ):

        #name = kwds.get("name", None)
        #temporaryName = kwds.pop("temporaryName", None)
        assert parent is not None, "NestedRefreshableList requires a parent RefreshableListInterface"
        kwds.setdefault('autoList',parent)
        Refreshable.__init__(self,mixinKwds=kwds)
        RefreshableListImplementation.__init__(self) #, name=name, temporaryName=temporaryName)
        self.__parent = parent

    def cleanup( self, context:EvaluationContext, when:TimeInSeconds) -> None:
        if self._dirtyCount > 0:
            self._sort(context,when)
    @property
    def nextRefreshAtTop(self) -> TimeInSeconds|None:
        if len(self._refreshables) == 0:
            return None
        return self._refreshables[0].nextRefresh
    
    def _nestedChanged(self, context:EvaluationContext) -> None:
        if len(self._refreshables) == 0:
            self.deactivate(context)
        else:
             self._dirtyCount += 1

    def _setNextListRefreshChanged(self,context:EvaluationContext,nextRefresh:Optional[TimeInSeconds]=None) -> None:
        """ Called when the next refresh time for the list changes. """
        super()._setNextListRefreshChanged(context, nextRefresh )

        self._nestedChanged( context )

    def refreshableCalculateNextRefresh(self, context:EvaluationContext, when:TimeInSeconds) -> TimeInSeconds|None:
        """ Calculate the next refresh time based on the current time and the refresh rate.
        """
        if len(self._refreshables) == 0:
            return None
        if self._dirtyCount > 0:
            self._sort(context,when)
        return self._refreshables[0].nextRefresh

    def derivedRefresh(self,context:EvaluationContext) -> None:
        if self._dirtyCount > 0:
            self._sort(context,context.when)
        
        self.process(context, context.when)
        if self._dirtyCount > 0:
            if self.refreshList:
                self.refreshList.markDirty(context,self)
            
        
#############################################################################

class NamedNestedRefreshableList(NestedRefreshableList,NamedLocalIdentifiable):
    
    class KWDS(NestedRefreshableList.KWDS,NamedLocalIdentifiable.KWDS):
        pass

    def __init__(self, parent:RefreshableListInterface, **kwds:Unpack[KWDS] ):
        nliKwds = NamedLocalIdentifiable.extractInitArgs(kwds)
        NestedRefreshableList.__init__(self, parent, **kwds)
        NamedLocalIdentifiable.__init__(self, **nliKwds)

#############################################################################

_sayImport.complete()
