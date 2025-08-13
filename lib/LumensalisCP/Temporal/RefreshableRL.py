from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( __name__, globals() )

# pyright: reportPrivateUsage=false, reportUnusedImport=false, reportUnusedFunction=false

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.util.Reloadable import ReloadableModule

if TYPE_CHECKING:
    from LumensalisCP.Eval.Expressions import EvaluationContext
    from LumensalisCP.Triggers.Invocable import Invocable, InvocableOrContextCB
    from LumensalisCP.Temporal.Refreshable import Refreshable
    from LumensalisCP.Temporal.Refreshable import RefreshableListInterface, \
          RfMxnActivatable, RfMxnInvocable, RfMxnPeriodic, RfMxnNamed
    from LumensalisCP.Temporal.RefreshableList import RefreshableListImplementation
    
#############################################################################

_module = ReloadableModule( 'LumensalisCP.Temporal.Refreshable' )
_listModule = ReloadableModule( 'LumensalisCP.Temporal.RefreshableList' )
_Refreshable = _module.reloadableClassMeta('Refreshable')
_RfMxnPeriodic = _module.reloadableClassMeta('RfMxnPeriodic')
_RfMxnActivatable = _module.reloadableClassMeta('RfMxnActivatable')
_RfMxnInvocable = _module.reloadableClassMeta('RfMxnInvocable')
_RfMxnNamed = _module.reloadableClassMeta('RfMxnNamed')
_RefreshableListImplementation = _listModule.reloadableClassMeta('RefreshableListImplementation')

#############################################################################

@_Refreshable.reloadableMethod()
def _refresh( self:Refreshable, context:EvaluationContext, when:TimeInSeconds ) -> bool:
        assert self.nextRefresh is not None
        if when >= self.nextRefresh:
            if self.enableDbgOut: self.dbgOut( "refreshing %s at %.3f", self, when )
            assert self.refreshList is not None
            self.__priorRefresh = self.__latestRefresh
            self.__latestRefresh = when
            self.__refreshCount += 1
            self.setNextRefresh( context, None )
            # self.__refreshList.markDirty(context, self)
            refreshList = self.refreshList
            try:
                self.derivedRefresh(context)
            except Exception as inst:
                refreshList.SHOW_EXCEPTION( inst, "derivedRefresh exception on %s", self )
                self.__latestException = inst
                self.__exceptionCount += 1
            now = context.newNow
            self.__latestRefreshComplete = now 
            
            if self.nextRefresh is None:
                if self.__autoRefresh:
                    nextRefresh = self.refreshableCalculateNextRefresh( context, now)
                    if self.enableDbgOut: self.dbgOut( "autoRefresh : %s", nextRefresh )
                    if nextRefresh is not None:
                        assert nextRefresh > now
                        self.setNextRefresh( context, nextRefresh )
                        #self.__refreshList.nextRefreshChanged(context, self)
                else:
                     if self.enableDbgOut: self.dbgOut( "expired, no autoRefresh" )

                if  self.nextRefresh is None:
                    assert self.refreshList is refreshList or self.refreshList is None, f"Refreshable {self} refresh list changed from {refreshList} to {self.refreshList}"
                
                    refreshList.remove(context, self)
                    
            return True # was processed
        
        assert self.refreshList is not None
        return False
    
@_Refreshable.reloadableMethod()
def __repr__(self:Refreshable) -> str:
    return f"{self.__class__.__name__}({getattr(self, 'name',self.dbgName)}, nextRefresh={self.nextRefresh}, refreshCount={self.__refreshCount}, latestRefresh={self.__latestRefresh})"

@_Refreshable.reloadableMethod()
def _clearNextRefresh( self:Refreshable, context:'EvaluationContext' ) -> None:
    if self.enableDbgOut: self.dbgOut( "clearNextRefresh()" )
    self.__nextRefresh = None
    if self.refreshList is not None:
        self.refreshList.markDirty(context, self)
        self.refreshList.nextRefreshChanged(context, self)


@_Refreshable.reloadableMethod()
def setNextRefresh( self:Refreshable, context:'EvaluationContext', when:TimeInSeconds ) -> None:
    assert when is not None
    if self.enableDbgOut: self.dbgOut( "setNextRefresh( %.3f )", when )
    self.__nextRefresh = when
    if self.refreshList is not None:
        self.refreshList.markDirty(context, self)
        self.refreshList.nextRefreshChanged(context, self)

@_Refreshable.reloadableMethod()
def _setRefreshList( self:Refreshable, context:'EvaluationContext', rl:RefreshableListImplementation ) -> None:
    self.__refreshList = rl

#############################################################################

_RfMxnPeriodic.reloadableMethod()
def setRefreshRate(self:RfMxnPeriodic, context:'EvaluationContext', refreshRate:TimeSpanInSeconds| Callable[[], TimeSpanInSeconds]) -> None:
        """ Set the refresh rate for this refreshable. """
        if callable(refreshRate):
            self.__refreshRate = refreshRate
        else:
            self.__refreshRate = TimeSpanInSeconds(refreshRate)
        self.refreshRateChanged(context)

_RfMxnPeriodic.reloadableMethod()
def refreshableCalculateNextRefresh(self:RfMxnPeriodic, context:'EvaluationContext', when:TimeInSeconds) -> TimeInSeconds|None:
        """ Calculate the next refresh time based on the current time and the refresh rate.
        """
        if callable(self.__refreshRate):
            return when + self.__refreshRate() # type: ignore[return-value]    
        return when + self.__refreshRate # type: ignore[return-value]

#############################################################################

@_RfMxnActivatable.reloadableMethod()    
def activate( self:RfMxnActivatable, context:Optional[EvaluationContext]=None, nextRefresh:Optional[TimeInSeconds]=None ) -> None:
        if context is None:
            context = getCurrentEvaluationContext()
        if self.enableDbgOut:  self.dbgOut(f"ActivatablePeriodicRefreshable.activate {self} nextRefresh={nextRefresh}")
        assert self.__autoList is not None, f"ActivatablePeriodicRefreshable {self} has no autoList"
        if nextRefresh is None:
            nextRefresh = self.refreshableCalculateNextRefresh(context, context.when)

        self.__autoList.add( context, self, nextRefresh=nextRefresh )
        self.__refreshIsActive = True

@_RfMxnActivatable.reloadableMethod()
def deactivate( self:RfMxnActivatable, context:'EvaluationContext' ) -> None:
        assert self.refreshList is not None
        self.refreshList.remove( context, self )
        self.__refreshIsActive = False
        self._setRefreshList(context,None)

#############################################################################

@_RfMxnInvocable.reloadableMethod()
def derivedRefresh(self:RfMxnInvocable, context:'EvaluationContext') -> None:
    self.__invocable(context)

#############################################################################


#############################################################################f


_sayImport.complete()
