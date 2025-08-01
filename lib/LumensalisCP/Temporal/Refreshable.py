from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( __name__, globals() )

# pyright: reportPrivateUsage=false, reportUnusedImport=false, reportUnusedFunction=false

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import NamedLocalIdentifiable

if TYPE_CHECKING:
    from  LumensalisCP.Eval.Expressions import EvaluationContext
    from LumensalisCP.Triggers.Invocable import Invocable, InvocableOrContextCB


#############################################################################

if TYPE_CHECKING:
    class RefreshableInterface(IDebuggable):
        @property
        def nextRefresh(self) -> TimeInSeconds|None: raise NotImplementedError

        def refreshableCalculateNextRefresh(self, context:'EvaluationContext', when:TimeInSeconds) -> TimeInSeconds|None: raise NotImplementedError
        def setNextRefresh( self, context:'EvaluationContext', when:TimeInSeconds ) -> None: raise NotImplementedError
        def refreshRateChanged(self,context:'EvaluationContext') -> None: ...
        
else:
    class RefreshableInterface: ...

#############################################################################

if TYPE_CHECKING:
    class RefreshableListInterface( IDebuggable ):
        class KWDS(NamedLocalIdentifiable.KWDS  ):
            pass

        def add( self,  context:EvaluationContext, item:RefreshableInterface|Refreshable, nextRefresh:Optional[TimeInSeconds]=None ) -> None:
            raise NotImplementedError( f"{self.__class__.__name__}.add not implemented" )

        def remove( self,  context:EvaluationContext, item:RefreshableInterface|Refreshable ) -> None:
            raise NotImplementedError( f"{self.__class__.__name__}.remove not implemented" )

        def markDirty( self, context:EvaluationContext, item:RefreshableInterface|Refreshable ) -> None:
            raise NotImplementedError( f"{self.__class__.__name__}.markDirty not implemented" )
        
        def nextRefreshChanged( self, context:EvaluationContext, item:RefreshableInterface|Refreshable ) -> None:
            raise NotImplementedError( f"{self.__class__.__name__}.markDirty not implemented" )
        
        
        def process( self, context:EvaluationContext, when:TimeInSeconds ) -> None:
                raise NotImplementedError( f"{self.__class__.__name__}.markDirty not implemented" )
else:
    class RefreshableListInterface: ...
    
#############################################################################

class Refreshable( RefreshableInterface, IDebuggable ):
    RFD_autoRefresh:ClassVar[bool] = False

    class KWDS(TypedDict):
        autoRefresh:NotRequired[bool]
        mixinKwds:NotRequired[StrAnyDict|Any]

    def __init__(self, autoRefresh:Optional[bool]=None, mixinKwds:Optional[StrAnyDict|Any]=None ) -> None:
        self.__refreshList:Optional[RefreshableListInterface] = None
        self.__nextRefresh:TimeInSeconds|None = None
        self.__refreshCount = 0
        self.__exceptionCount = 0
        self.__latestException:Exception|None = None
        self.__latestRefresh:TimeInSeconds|None = None
        self.__priorRefresh:TimeInSeconds|None = None
        self.__latestRefreshComplete:TimeInSeconds|None = None


        self.__autoRefresh:bool = self.RFD_autoRefresh if autoRefresh is None else autoRefresh
        if mixinKwds is not None:
            assert isinstance(mixinKwds, dict), "Mixin keywords must be a dictionary"
            self._mixins_init(mixinKwds) # type: ignore[call-arg]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r}, nextRefresh={self.__nextRefresh}, refreshCount={self.__refreshCount}, latestRefresh={self.__latestRefresh})"
    #def refreshableCalculateNextRefresh(self, context:'EvaluationContext', when:TimeInSeconds) -> TimeInSeconds|None:
    #    """ Calculate the next refresh time based on the current time and the refresh rate.
    #    """
    #    raise NotImplementedError

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
                self.derivedRefresh(context)
            except Exception as inst:
                refreshList.SHOW_EXCEPTION( inst, "derivedRefresh exception on %s", self )
                self.__latestException = inst
                self.__exceptionCount += 1
            now = context.newNow
            self.__latestRefreshComplete = now 
            if  self.__nextRefresh is None:
                assert self.__refreshList is refreshList
                if self.__autoRefresh:
                    nextRefresh = self.refreshableCalculateNextRefresh( context, now)
                    if self.enableDbgOut: self.dbgOut( "autoRefresh : %s", nextRefresh )
                    if nextRefresh is not None:
                        assert nextRefresh > now
                        self.__nextRefresh = nextRefresh
                        self.__refreshList.nextRefreshChanged(context, self)

            if  self.__nextRefresh is None:
                refreshList.remove(context, self)
                
            return True # was processed
        
        assert self.__refreshList is not None
        return False
    
    @property
    def nextRefresh(self) -> TimeInSeconds|None: return self.__nextRefresh
    @property
    def priorRefresh(self) -> TimeInSeconds|None: return self.__priorRefresh
    @property
    def latestRefresh(self) -> TimeInSeconds|None: return self.__latestRefresh
    @property
    def latestRefreshComplete(self) -> TimeInSeconds|None: return self.__latestRefreshComplete

    def setNextRefresh( self, context:'EvaluationContext', when:TimeInSeconds ) -> None:
        self.__nextRefresh = when
        if self.__refreshList is not None:
            self.__refreshList.markDirty(context, self)

    def derivedRefresh(self,context:'EvaluationContext') -> None:
        raise NotImplementedError

    def refreshRateChanged(self,context:'EvaluationContext') -> None:
        pass

    def __mixins_init_base(self, cls:type, kwargs:StrAnyDict):
        if cls.__dict__.get( '_mixin_init',None) is not None:
            # cls is a mixin, call its _mixin_init 
            cls._mixin_init(self, kwargs) # type: ignore[return-value]
        # check base classes
        for base in cls.__bases__:
            self.__mixins_init_base( base, kwargs)

    def _mixins_init(self, kwargs:StrAnyDict) -> StrAnyDict:
        #print( f"_mixins_init called for {self.__class__.__name__} with kwargs={kwargs}" )
        for base in self.__class__.__bases__:
            self.__mixins_init_base(base, kwargs)
        #print( f"  returning kwargs={kwargs}" )
        return kwargs # type: ignore[return-value]

#############################################################################
class RfMxn(RefreshableInterface): ...

#############################################################################

class RfMxnPeriodic(RfMxn):
    RFD_refreshRate:ClassVar[TimeSpanInSeconds] = 0.33

    class KWDS(TypedDict):
        refreshRate:NotRequired[TimeSpanInSeconds| Callable[[], TimeSpanInSeconds]]

    def _mixin_init(self,kwargs:StrAnyDict) -> None:
        refreshRate = kwargs.pop('refreshRate', self.RFD_refreshRate)
        self.__refreshRate:TimeSpanInSeconds| Callable[[], TimeSpanInSeconds] = refreshRate

    def setRefreshRate(self, context:'EvaluationContext', refreshRate:TimeSpanInSeconds| Callable[[], TimeSpanInSeconds]) -> None:
        """ Set the refresh rate for this refreshable. """
        if callable(refreshRate):
            self.__refreshRate = refreshRate
        else:
            self.__refreshRate = TimeSpanInSeconds(refreshRate)
        self.refreshRateChanged(context)


    def refreshableCalculateNextRefresh(self, context:'EvaluationContext', when:TimeInSeconds) -> TimeInSeconds|None:
        """ Calculate the next refresh time based on the current time and the refresh rate.
        """
        if callable(self.__refreshRate):
            return when + self.__refreshRate() # type: ignore[return-value]    
        return when + self.__refreshRate # type: ignore[return-value]

#############################################################################

class RfMxnActivatable(RfMxn):
    class KWDS(TypedDict):
        autoList:NotRequired[RefreshableListInterface]

    def _mixin_init(self,kwargs:StrAnyDict) -> None:
        self.__autoList:RefreshableListInterface|None =  kwargs.pop('autoList', None)

    def activate( self, context:Optional[EvaluationContext]=None, nextRefresh:Optional[TimeInSeconds]=None ) -> None:
        if context is None:
            context = getCurrentEvaluationContext()
        if self.enableDbgOut:  self.dbgOut(f"ActivatablePeriodicRefreshable.activate {self} nextRefresh={nextRefresh}")
        assert self.__autoList is not None, f"ActivatablePeriodicRefreshable {self} has no autoList"
        if nextRefresh is None:
            nextRefresh = self.refreshableCalculateNextRefresh(context, context.when)
        self.__autoList.add( context, self, nextRefresh=nextRefresh )
    
    def deactivate( self, context:'EvaluationContext' ) -> None:
        assert self.__autoList is not None
        self.__autoList.remove( context, self )

#############################################################################

class RfMxnActivatablePeriodic(RfMxnActivatable, RfMxnPeriodic):
    class KWDS(RfMxnActivatable.KWDS, RfMxnPeriodic.KWDS):
        pass
        
    def _mixin_init(self,kwargs:StrAnyDict) -> None:
        RfMxnActivatable._mixin_init(self, kwargs)
        RfMxnPeriodic._mixin_init(self, kwargs)

#############################################################################

class RfMxnInvocable(RfMxn):
    class KWDS(TypedDict):
        invocable:Required[InvocableOrContextCB]

    def _mixin_init(self,kwargs:StrAnyDict) -> None:
        invocable = kwargs.pop('invocable', None)  # type: ignore[assignment]
        assert invocable is not None, "RfMxnInvocable requires an invocable"
        self.__invocable:InvocableOrContextCB =  invocable

    def derivedRefresh(self,context:'EvaluationContext') -> None:
        self.__invocable(context)

#############################################################################

class RfMxnNamed( NamedLocalIdentifiable, RfMxn ):

    def _mixin_init(self,  kwargs:StrAnyDict ):
        nliKwds = NamedLocalIdentifiable.extractInitArgs(kwargs)
        NamedLocalIdentifiable.__init__(self, **nliKwds)

#############################################################################

class PeriodicRefreshable( RfMxnPeriodic,Refreshable ):
    RFD_autoRefresh:ClassVar[bool] = True

    class KWDS(Refreshable.KWDS, RfMxnPeriodic.KWDS):
        pass
    
    def __init__(self, **kwargs:Unpack[KWDS] ) -> None:
        #RfMxnPeriodic._mixin_init(self, kwargs)
        Refreshable.__init__(self, mixinKwds=kwargs)


#############################################################################
# pyright: reportPrivateUsage=false

class ActivatablePeriodicRefreshable( RfMxnActivatable, RfMxnPeriodic, Refreshable ):
    RFD_autoRefresh:ClassVar[bool] = True
   
    class KWDS(Refreshable.KWDS, RfMxnActivatable.KWDS, RfMxnPeriodic.KWDS):
        pass

    def __init__(self, **kwargs:Unpack[KWDS] ) -> None:
        #RfMxnActivatable._mixin_init(self, kwargs)
        #RfMxnPeriodic._mixin_init(self, kwargs)
        Refreshable.__init__(self, mixinKwds=kwargs)

#############################################################################

class RefreshablePrdInvAct( RfMxnInvocable,
                            RfMxnActivatable, 
                            RfMxnPeriodic, 
                            RfMxnNamed,
                            Refreshable 
                        ):
    RFD_autoRefresh:ClassVar[bool] = True

    class KWDS(Refreshable.KWDS, 
               NamedLocalIdentifiable.KWDS,
               RfMxnInvocable.KWDS,
               RfMxnActivatable.KWDS,
               RfMxnPeriodic.KWDS
            ):
        pass

    def __init__(self, **kwargs:Unpack[KWDS] ) -> None:
        #nliKwds = NamedLocalIdentifiable.extractInitArgs(kwargs)
        #RfMxnNamed._mixin_init(self, kwargs)
        #RfMxnInvocable._mixin_init(self, kwargs)
        #RfMxnActivatable._mixin_init(self, kwargs)
        #RfMxnPeriodic._mixin_init(self, kwargs)
        Refreshable.__init__(self, mixinKwds=kwargs)


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

class NamedPeriodicRefreshable( NamedLocalIdentifiable, PeriodicRefreshable ):
    class KWDS(PeriodicRefreshable.KWDS, NamedLocalIdentifiable.KWDS):
        pass
    def __init__(self,  **kwargs:Unpack[PeriodicRefreshable.KWDS] ):

        nliKwds = NamedLocalIdentifiable.extractInitArgs(kwargs)
        NamedLocalIdentifiable.__init__(self, **nliKwds)
        PeriodicRefreshable.__init__(self, **kwargs)

#############################################################################f

__all__ = [
    'Refreshable',
    'RefreshableListInterface',
    'PeriodicRefreshable',
    'ActivatablePeriodicRefreshable',
    'ManualRefreshable',
    'NamedPeriodicRefreshable',
    'RefreshablePrdInvAct',
    'RefreshableInterface',
    'RfMxn',
    'RfMxnPeriodic',
    'RfMxnActivatable',
    'RfMxnActivatablePeriodic',
    'RfMxnInvocable',
    'RfMxnNamed',
]

_sayImport.complete()
