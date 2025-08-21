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

_listModule = ReloadableModule( 'LumensalisCP.Temporal.RefreshableList' )

_RefreshableListImplementation = _listModule.reloadableClassMeta('RefreshableListImplementation')

#############################################################################

#############################################################################


@_RefreshableListImplementation.reloadableMethod()
def __processOne( self:RefreshableListImplementation, context:EvaluationContext, when:TimeInSeconds, item:Refreshable, index:int ) -> None:  
        show = self.enableDbgOut or item.enableDbgOut
        
        # prepare for refresh
        assert item.refreshList is self
        item.__priorRefresh = item.__latestRefresh
        item.__latestRefresh = when
        item.__refreshCount += 1
        item._clearNextRefresh(context)
        
        try:
            item.derivedRefresh(context)
        except Exception as inst:
            item.SHOW_EXCEPTION( inst, "derivedRefresh exception in %s", self )
            item.__latestException = inst
            item.__exceptionCount += 1

        # handle list rescheduling
        if item.nextRefresh is None:  # should normally be true, unless
                # the item's derivedRefresh ended up calling setNextRefresh
            
            if item.__autoRefresh:
                nextRefresh = item.refreshableCalculateNextRefresh(context, when)
                if show: self.dbgOut( "autoRefresh %s at %s", item, nextRefresh )
                if nextRefresh is not None:
                    #assert nextRefresh > when, f"nextRefresh {nextRefresh} not after now {when}"
                    item.setNextRefresh(context, nextRefresh)
            else:
                if self.enableDbgOut: self.dbgOut( "expired, no autoRefresh" )


#@_RefreshableListImplementation.reloadableMethod()
def _processInner( self:RefreshableListImplementation, context:EvaluationContext, when:TimeInSeconds ) -> None:
        self.__processCount += 1
        if len(self._refreshables) == 0: 
            if self.enableDbgOut: self.dbgOut( "no refreshables to process" )  
            return 
        if self._dirtyCount > 0:
            self._sort(context,when)
        
        #self.__assertSorted()
        first = self._refreshables[0]
        assert first.nextRefresh is not None, f"Top item {first} has no next refresh time"
        show = self.enableDbgOut or first.enableDbgOut
        if first.nextRefresh > when:
            if show: self.dbgOut( "process not ready, nextRefresh = %.3f > %.3f", first.nextRefresh, when )  
            return

        if show: self.infoOut("process refreshing %r", first)
        #top._refresh(context, when)
        self.__processOne(context, when, first,0)
        nextRefresh = first.nextRefresh
        if nextRefresh is None: # type: ignore[assignment]
            removed = self._refreshables.pop(0) 
            assert removed is first, f"Removed item {removed} is not the top item {first}"
            if len(self._refreshables) >= 0:
                nextRefresh = self._refreshables[0].nextRefresh
        else:
            # changed, but does it move?
            if len(self._refreshables) > 1:
                if self._refreshables[0] is not first:
                    self.errOut("process nextRefresh %s but top(%r) is not [0](%r) of %d",
                                  nextRefresh, first, self._refreshables[0], len(self._refreshables))
                    self.markDirty(context, first)  
                elif self._refreshables[1].nextRefresh is not None:
                    if nextRefresh <= self._refreshables[1].nextRefresh:
                        if show: self.infoOut("process nextRefresh %s is not moving", nextRefresh)
                    else:
                        # out of order but...
                        removed = self._refreshables.pop(0) 
                        assert removed is first, f"Removed item {removed} is not the top item {first}"
                        nextRefresh = self._refreshables[0].nextRefresh
                        if first.nextRefresh >= self._refreshables[-1].nextRefresh:
                            # moving to end maintains sort
                            if show: self.infoOut("process nextRefresh %s moving to end", nextRefresh)
                            self._refreshables.append(first)
                        else:
                            if show: self.infoOut("process nextRefresh %s requires sort", nextRefresh)
                            self._refreshables.append(first)
                            self.markDirty(context, first)

        #if nextRefresh is not None:
        if self._dirtyCount:
            self.processFinishedDirty(context)
        else:
            if nextRefresh != self._nextListRefresh:
                self._setNextListRefreshChanged(context, nextRefresh)

        if show:
            self.infoOut("process finished, nextRefresh = %s, dirty=%s", nextRefresh, self._dirtyCount)
            assert nextRefresh == self._nextListRefresh or self._dirtyCount > 0, f"nextRefresh {nextRefresh} != _nextListRefresh {self._nextListRefresh} dirty={self._dirtyCount}"

@_RefreshableListImplementation.reloadableMethod()
def process( self:RefreshableListImplementation, context:EvaluationContext, when:TimeInSeconds ) -> None:
    _processInner(self, context, when)
    if self._nextListRefresh is None or self._nextListRefresh > when: return 

    extra = 0 
    while extra < 3 and self._nextListRefresh <= when :
        extra += 1
        if self.enableDbgOut: self.infoOut("process extra %r: nextListRefresh %s <= when %s ...", extra, self._nextListRefresh, when)
        self.__extraCount += 1

        _processInner(self, context, when)
        


@_RefreshableListImplementation.reloadableMethod()
def addActive( self:RefreshableListImplementation, context:EvaluationContext, item:Refreshable, nextRefresh:Optional[TimeInSeconds]=None ) -> None:
    self.add( context, item, nextRefresh )
    assert hasattr(item, 'autoList')
    autoList = getattr( item, 'autoList', None)
    if autoList is not None:
        assert autoList is self
    else:
        item.__autoList = self

@_RefreshableListImplementation.reloadableMethod()
def add( self:RefreshableListImplementation, context:EvaluationContext, item:Refreshable, nextRefresh:Optional[TimeInSeconds]=None ) -> None:
    if item.refreshList is not None:
        if item.refreshList is not self:
            raise ValueError( f"Item {item} already in a refresh list {item.refreshList}" )
        self.warnOut( "add ... Item %s already in this refresh list", item )
    
    if nextRefresh is None:
        nextRefresh = item.refreshableCalculateNextRefresh(context, context.when)
        assert nextRefresh is not None, f"Refreshable {item} did not calculate a next refresh time"
    
    showDbg = self.enableDbgOut or item.enableDbgOut
    # call BEFORE setting item.__refreshList
    if showDbg: self.infoOut( "adding %r at %.3f", item, nextRefresh )

    item.setNextRefresh(context, nextRefresh)
    item._setRefreshList(context, self)


    if self._nextListRefresh is None:
        # adding to an empty list
        if showDbg: self.infoOut( "adding %r at %.3f to empty list", item, nextRefresh )
        assert len(self._refreshables) == 0, "Adding to an empty list but list is not empty"
        self._refreshables.append(item)
        self._setNextListRefreshChanged(context,nextRefresh)

    elif nextRefresh < self._nextListRefresh:
        # adding to the front of the list
        if showDbg: self.infoOut( "adding %r at %.3f at front of list", item, nextRefresh )
        self._refreshables.insert(0, item)  # insert at the front
        self._setNextListRefreshChanged(context,nextRefresh)
    else:

        assert self._refreshables[-1].nextRefresh is not None
        if nextRefresh >= self._refreshables[-1].nextRefresh: # type: ignore[reportAttributeAccessIssue]
            if showDbg: self.infoOut("adding %r at %.3f at end of list", item, nextRefresh )
            # adding to the end of the list
            self._refreshables.append(item)
        else:
            # adding somewhere in the middle, mark dirty
            if showDbg: self.infoOut("adding %r at %.3f in interior of list", item, nextRefresh )
            self._refreshables.append(item)
            self.markDirty(context, item)

@_RefreshableListImplementation.reloadableMethod()
def _setNextListRefreshChanged(self:RefreshableListImplementation,context:EvaluationContext,nextRefresh:Optional[TimeInSeconds]=None) -> None:
    """ Called when the next refresh time for the list changes. """
    if self.enableDbgOut:
        if nextRefresh is None: self.dbgOut( "_setNextListRefreshChanged None" )
        else:   self.dbgOut( "_setNextListRefreshChanged %.3f", nextRefresh )
    self._nextListRefresh = nextRefresh

@_RefreshableListImplementation.reloadableMethod()
def remove( self:RefreshableListImplementation,  context:EvaluationContext, item:Refreshable ) -> None:
    assert len(self._refreshables) > 0, "Cannot remove from empty refresh list"
    assert item.refreshList is self, f"Item {item} is in a different refresh list {item.refreshList}"

    # remove should not change the sort order, so we don't need
    # to mark dirty...
    
    if self._refreshables[0] is item:
        # removing from the front of the list
        self._refreshables.pop(0)
        if self.enableDbgOut or item.enableDbgOut:
            self.infoOut("Removing item from front of list: %s", item)
        if len(self._refreshables) > 0:
            nextListRefresh = self._refreshables[0].nextRefresh
            self._setNextListRefreshChanged(context,nextListRefresh)
    else:
        if self.enableDbgOut or item.enableDbgOut:
            self.infoOut("Removing item from front of list: %s", item)
        self._refreshables.remove(item)
        item._setRefreshList( context, None )

@_RefreshableListImplementation.reloadableMethod()
def nextRefreshChanged( self:RefreshableListImplementation, context:EvaluationContext, item:Refreshable ) -> None:
    if len(self._refreshables) == 1:
        assert self._refreshables[0] is item, f"Next refresh changed but only one item in list {self._refreshables[0]} is not {item}"
        if self.enableDbgOut or item.enableDbgOut: self.infoOut("nextRefreshChanged: %s (%r)", item, item.nextRefresh)
        self._setNextListRefreshChanged(context,item.nextRefresh)
        return 
    pass

@_RefreshableListImplementation.reloadableMethod()
def getNextRefreshForList(self:RefreshableListImplementation, context:EvaluationContext, when:TimeInSeconds) -> TimeInSeconds|None:
    if len(self._refreshables) == 0:
        return None
    if self._dirtyCount > 0:
        self._sort(context,context.when)

    nextRefresh = self._refreshables[0].nextRefresh
    if nextRefresh != self._nextListRefresh:
        self._nextListRefresh = nextRefresh
        self._setNextListRefreshChanged(context)
    return nextRefresh

@_RefreshableListImplementation.reloadableMethod()
def markDirty( self:RefreshableListImplementation, context:EvaluationContext, item:Refreshable|None ) -> None:
    self._dirtyCount += 1

@_RefreshableListImplementation.reloadableMethod()
def _sort(self:RefreshableListImplementation, context:EvaluationContext, when:TimeInSeconds) -> None:
    if self.enableDbgOut: self.dbgOut( "sorting, dirtyCount = %d", self._dirtyCount )
    
    def _refreshableSortKey(item:Refreshable) -> TimeInSeconds:
        nextRefresh = item.nextRefresh
        if nextRefresh is None:
            nextRefresh = item.refreshableCalculateNextRefresh(context, when)
        return item.nextRefresh or 9999999999999.9 # type: ignore[return-value]
    self._refreshables.sort(key=_refreshableSortKey)
    self._dirtyCount = 0
    self._sortCount += 1

#############################################################################f


_sayImport.complete()
