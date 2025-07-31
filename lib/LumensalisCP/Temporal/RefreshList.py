from collections import deque
from tkinter import N
from .Refreshable import Refreshable, RefreshList

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
import collections.deque

# pyright: reportPrivateUsage=false

if TYPE_CHECKING:
    from  LumensalisCP.Eval.Expressions import EvaluationContext

#############################################################################

def _refeshableSortKey(item:Refreshable) -> TimeInSeconds:
    return item.__nextRefresh or 9999999999999.9 # type: ignore[return-value]

class RefreshListImplementation( RefreshList ):
    
    class KWDS(NamedLocalIdentifiable.KWDS):
        maxLen: NotRequired[int]

    def __init__(self, maxLen:int=100, **kwds:Unpack[RefreshList.KWDS] ):
        self._dirtyCount = 0
        self._sortCount = 0
        #self._refreshables:deque[Refreshable] = deque(maxlen=maxLen,flag=True)
        self._refreshables:list[Refreshable] = []
        

        self._nextListRefresh:TimeInSeconds|None = None

    def add( self, context:EvaluationContext, item:Refreshable, nextRefresh:Optional[TimeInSeconds]=None ) -> None:
        if item.__refreshList is not None:
            raise ValueError( f"Item {item} already in a refresh list {item.__refreshList}" )
        
        if nextRefresh is None:
            nextRefresh = item.refreshableCalculateNextRefresh(context, context.when)
            assert nextRefresh is not None, f"Refreshable {item} did not calculate a next refresh time"
        
        # call BEFORE setting item.__refreshList
        item.setNextRefresh(context, nextRefresh)
        item.__refreshList = self


        if self._nextListRefresh is None:
            # adding to an empty list
            assert len(self._refreshables) == 0, "Adding to an empty list but list is not empty"
            self._refreshables.append(item)
            self._setNextListRefreshChanged(nextRefresh)

        elif nextRefresh < self._nextListRefresh:
            # adding to the front of the list
            self._refreshables.insert(0, item)  # insert at the front
            self._setNextListRefreshChanged(nextRefresh)
        else:

            assert self._refreshables[-1].__nextRefresh is not None
            if nextRefresh >= self._refreshables[-1].__nextRefresh: # type: ignore[reportAttributeAccessIssue]
                # adding to the end of the list
                self._refreshables.append(item)
            else:
                # adding somewhere in the middle, mark dirty
                self._refreshables.append(item)
                self.markDirty(context, item)

    def _setNextListRefreshChanged(self,nextRefresh:Optional[TimeInSeconds]=None) -> None:
        """ Called when the next refresh time for the list changes. """
        self._nextListRefresh = nextRefresh

    def remove( self,  context:EvaluationContext, item:Refreshable ) -> None:
        assert len(self._refreshables) > 0, "Cannot remove from empty refresh list"
        assert item.__refreshList is self, f"Item {item} is in a different refresh list {item.__refreshList}"

        # remove should not change the sort order, so we don't need
        # to mark dirty...
        
        if self._refreshables[0] is item:
            # removing from the front of the list
            self._refreshables.pop(0)
            if len(self._refreshables) > 0:
                nextListRefresh = self._refreshables[0].__nextRefresh
                self._setNextListRefreshChanged(nextListRefresh)
        else:
            self._refreshables.remove(item)
            item.__refreshList = None

    def markDirty( self, context:EvaluationContext, item:Refreshable|None ) -> None:
        self._dirtyCount += 1

    def _sort(self) -> None:
        self._refreshables.sort(key=_refeshableSortKey)
        self._dirtyCount = 0
        self._sortCount += 1

class RootRefreshList(RefreshListImplementation):
    pass


class NestedRefreshList(RefreshListImplementation, Refreshable):
    class KWDS(Refreshable.KWDS,NamedLocalIdentifiable.KWDS):
        pass

    def __init__(self, parent:RefreshList, **kwds:Unpack[RefreshList.KWDS] ):

        name = kwds.get("name", None)
        temporaryName = kwds.pop("temporaryName", None)
        Refreshable().__init__(**kwds)
        RefreshListImplementation.__init__(self, name=name, temporaryName=temporaryName)
        self.__parent = parent


    def doRefresh(self,context:'EvaluationContext') -> None:
        raise NotImplementedError        