from __future__ import annotations

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import NamedLocalIdentifiable

if TYPE_CHECKING:
    from  LumensalisCP.Eval.Expressions import EvaluationContext

#############################################################################

#############################################################################

class RefreshList( NamedLocalIdentifiable ):
    
    def add( self,  context:EvaluationContext, item:Refreshable, nextRefresh:Optional[TimeInSeconds]=None ) -> None:
        raise NotImplementedError
    
    def remove( self,  context:EvaluationContext, item:Refreshable ) -> None:
        raise NotImplementedError

    def markDirty( self, context:EvaluationContext, item:Refreshable ) -> None:
        raise NotImplementedError

#############################################################################

class Refreshable( object ):

    class KWDS(TypedDict):
        autoRefresh:NotRequired[bool]
        

    def __init__(self, autoRefresh:bool=False ):
        self.__refreshList:Optional[RefreshList] = None
        self.__nextRefresh:TimeInSeconds|None = None
        self.__refreshCount = 0
        self.__exceptionCount = 0
        self.__latestException:Exception|None = None
        self.__latestRefresh:TimeInSeconds|None = None
        self.__priorRefresh:TimeInSeconds|None = None
        self.__autoRefresh = autoRefresh

    def refreshableCalculateNextRefresh(self, context:'EvaluationContext', when:TimeInSeconds) -> TimeInSeconds|None:
        """ Calculate the next refresh time based on the current time and the refresh rate.
        """
        raise NotImplementedError

    @final
    def _refresh( self, context:EvaluationContext, when:TimeInSeconds ) -> bool:
        assert self.__nextRefresh is not None
        if when >= self.__nextRefresh:
            assert self.__refreshList is not None
            self.__priorRefresh = self.__latestRefresh
            self.__latestRefresh = when
            self.__refreshCount += 1
            self.__nextRefresh = None
            self.__refreshList.markDirty(context, self)
            refreshList = self.__refreshList
            try:
                self.doRefresh(context)
            except Exception as inst:
                refreshList.SHOW_EXCEPTION( inst, "Refreshable.doRefresh exception on %s", self )
                self.__latestException = inst
                self.__exceptionCount += 1

            if  self.__nextRefresh is None:
                assert self.__refreshList is refreshList
                if self.__autoRefresh:
                    nextRefresh = self.refreshableCalculateNextRefresh( context, when)
                    if nextRefresh is not None:
                        self.__nextRefresh = nextRefresh
                        self.__refreshList.markDirty(context, self)

            if  self.__nextRefresh is None:
                refreshList.remove(context, self)
                
            return True # was processed
        
        assert self.__refreshList is not None
        return False
    
    @property
    def nextRefresh(self) -> TimeInSeconds|None:
        return self.__nextRefresh

    def setNextRefresh( self, context:'EvaluationContext', when:TimeInSeconds ) -> None:
        self.__nextRefresh = when
        if self.__refreshList is not None:
            self.__refreshList.markDirty(context, self)

    def doRefresh(self,context:'EvaluationContext') -> None:
        raise NotImplementedError

#############################################################################

class PeriodicRefreshable( Refreshable ):

    class KWDS(Refreshable.KWDS):
        refreshRate:NotRequired[TimeInSeconds]
    
    def __init__(self, 
                 refreshRate:TimeInSeconds = 0.33,  # type: ignore[assignment]
                 **kwargs:Unpack[Refreshable.KWDS]
            ) -> None:
        super().__init__(**kwargs)

        self.__autoRefresh = True
        self.__refreshRate = refreshRate
        


    def refreshableCalculateNextRefresh(self, context:'EvaluationContext', when:TimeInSeconds) -> TimeInSeconds|None:
        """ Calculate the next refresh time based on the current time and the refresh rate.
        """
        return when + self.__refreshRate # type: ignore[return-value]

   

#############################################################################

class ManualRefreshable( Refreshable ):

    #class KWDS(Refreshable.KWDS):
    #    pass
    
    def __init__(self, **kwargs:Unpack[Refreshable.KWDS] ):
        super().__init__(**kwargs)
        


    def refreshableCalculateNextRefresh(self, context:'EvaluationContext', when:TimeInSeconds) -> TimeInSeconds|None:
        """ Calculate the next refresh time based on the current time and the refresh rate.
        """
        return None


#############################################################################
