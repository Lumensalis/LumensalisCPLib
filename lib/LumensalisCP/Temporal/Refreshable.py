from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( __name__, globals() )

# pyright: reportPrivateUsage=false, reportUnusedImport=false, reportUnusedFunction=false

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.util.Reloadable import ReloadableClass, reloadingMethod
from . import RefreshableRL
if TYPE_CHECKING:
    from  LumensalisCP.Eval.Expressions import EvaluationContext
    from LumensalisCP.Triggers.Invocable import Invocable, InvocableOrContextCB

#############################################################################

if TYPE_CHECKING:
    from LumensalisCP.Temporal.RefreshableList import RefreshableListImplementation

    class RefreshableInterface(IDebuggable):
        @property
        def nextRefresh(self) -> TimeInSeconds|None: raise NotImplementedError

        def refreshableCalculateNextRefresh(self, context:'EvaluationContext', when:TimeInSeconds) -> TimeInSeconds|None: ...
        def setNextRefresh( self, context:'EvaluationContext', when:TimeInSeconds|None ) -> None: ...
        def refreshRateChanged(self,context:'EvaluationContext') -> None: ...
        
        __refreshList:RefreshableListInterface|None

else:
    class RefreshableInterface: ...

#############################################################################

if TYPE_CHECKING:
    class RefreshableListInterface( IDebuggable ):


        def add( self,  context:EvaluationContext, item:Refreshable, nextRefresh:Optional[TimeInSeconds]=None ) -> None:
            raise NotImplementedError( f"{self.__class__.__name__}.add not implemented" )

        def remove( self,  context:EvaluationContext, item:Refreshable ) -> None:
            raise NotImplementedError( f"{self.__class__.__name__}.remove not implemented" )

        def markDirty( self, context:EvaluationContext, item:Refreshable ) -> None:
            raise NotImplementedError( f"{self.__class__.__name__}.markDirty not implemented" )
        
        def nextRefreshChanged( self, context:EvaluationContext, item:Refreshable ) -> None:
            raise NotImplementedError( f"{self.__class__.__name__}.markDirty not implemented" )
        
        
        def process( self, context:EvaluationContext, when:TimeInSeconds ) -> None:
            raise NotImplementedError( f"{self.__class__.__name__}.markDirty not implemented" )
        
        def cleanup( self, context:EvaluationContext, when:TimeInSeconds) -> None:
            raise NotImplementedError( f"{self.__class__.__name__}.cleanup not implemented" )
else:
    class RefreshableListInterface: ...
    
#############################################################################

@ReloadableClass([RefreshableRL])
class Refreshable( RefreshableInterface, IDebuggable ):
    RFD_autoRefresh:ClassVar[bool] = False

    class KWDS(TypedDict):
        autoRefresh:NotRequired[bool]
        mixinKwds:NotRequired[StrAnyDict]

    def __init__(self, autoRefresh:Optional[bool]=None, mixinKwds:Optional[StrAnyDict]=None ) -> None:

        self.__refreshList:RefreshableListImplementation|None = None
        self.__nextRefresh:TimeInSeconds|None = None
        self.__refreshCount = 0
        self.__exceptionCount = 0
        self.__latestException:Exception|None = None
        self.__latestRefresh:TimeInSeconds|None = None
        self.__priorRefresh:TimeInSeconds|None = None
        self.__latestRefreshComplete:TimeInSeconds|None = None


        if mixinKwds is not None:
            assert isinstance(mixinKwds, dict), "Mixin keywords must be a dictionary"
            if autoRefresh is None: 
                autoRefresh = mixinKwds.pop('autoRefresh', self.RFD_autoRefresh)

            self._mixins_init(mixinKwds) # type: ignore[call-arg]
        
        if autoRefresh is None:
            autoRefresh = self.RFD_autoRefresh
        
        self.__autoRefresh:bool = autoRefresh

    @property
    def refreshCount(self) -> int:
        return self.__refreshCount

    @property
    def exceptionCount(self) -> int:
        return self.__exceptionCount

    @reloadingMethod
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({getattr(self, 'name',self.dbgName)}, nextRefresh={self.nextRefresh}, refreshCount={self.__refreshCount}, latestRefresh={self.__latestRefresh})"
    #def refreshableCalculateNextRefresh(self, context:'EvaluationContext', when:TimeInSeconds) -> TimeInSeconds|None:
    #    """ Calculate the next refresh time based on the current time and the refresh rate.
    #    """
    #    raise NotImplementedError

    @final
    @reloadingMethod
    def _refresh( self, context:EvaluationContext, when:TimeInSeconds ) -> bool: ...
  
    @property
    def nextRefresh(self) -> TimeInSeconds|None: 
        return self.__nextRefresh
    
    @property
    def priorRefresh(self) -> TimeInSeconds|None: 
        return self.__priorRefresh
    
    @property
    def latestRefresh(self) -> TimeInSeconds|None: 
        return self.__latestRefresh
    
    @property
    def latestRefreshComplete(self) -> TimeInSeconds|None:
        return self.__latestRefreshComplete
    
    @property
    def refreshList(self) -> RefreshableListImplementation|None:
        return self.__refreshList

    @reloadingMethod
    def setNextRefresh( self, context:'EvaluationContext', when:TimeInSeconds|None ) -> None: ...

    @reloadingMethod
    def _clearNextRefresh( self, context:'EvaluationContext' ) -> None: ...

    @reloadingMethod
    def _setRefreshList( self, context:'EvaluationContext', rl:RefreshableListImplementation ) -> None: ...

    def derivedRefresh(self,context:'EvaluationContext') -> None:
        raise NotImplementedError( f"{self.__class__.__name__}.derivedRefresh not implemented")

    def refreshRateChanged(self,context:'EvaluationContext') -> None:
        pass

    def refreshableCalculateNextRefresh(self, context:'EvaluationContext', when:TimeInSeconds) -> TimeInSeconds|None:
        return None

    def __mixins_init_base(self, cls:type, kwargs:StrAnyDict):
        if cls.__dict__.get( '_mixin_init',None) is not None:
            # cls is a mixin, call its _mixin_init 
            if self._debugMixins: print( f"Calling _mixin_init for {cls.__name__} with kwargs={kwargs}" )
            cls._mixin_init(self, kwargs) # type: ignore[return-value]
        # check base classes
        for base in cls.__bases__:
            self.__mixins_init_base( base, kwargs)

    _debugMixins:bool = False
    def _mixins_init(self, kwargs:StrAnyDict) -> StrAnyDict:
        if self._debugMixins: print( f"_mixins_init called for {self.__class__.__name__} with kwargs={kwargs}" )
        for base in self.__class__.__bases__:
            self.__mixins_init_base(base, kwargs)
        if self._debugMixins: print( f"  returning kwargs={kwargs}" )
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
            rr = self.__refreshRate()  # type: ignore[call-arg]
        else:
            rr = self.__refreshRate
        rv = TimeInSeconds(rr + when)
        if self.enableDbgOut:
            self.dbgOut( "refreshableCalculateNextRefresh %.3f + %.3f = %.3f", when, rr, rv)
            
        return rv 

#############################################################################

class RfMxnActivatable(RfMxn):
    class KWDS(TypedDict):
        autoList:NotRequired[RefreshableListInterface]

    def _mixin_init(self,kwargs:StrAnyDict) -> None:
        self.__autoList:RefreshableListInterface|None =  kwargs.pop('autoList', None)
        #assert self.__autoList is not None, f"{self.__class__.__name__} requires an autoList"
        self.__refreshIsActive:bool = False

    @property
    def autoList(self) -> RefreshableListInterface|None:
        """ The list of refreshables that this refreshable is part of. """
        return self.__autoList
    
    @property
    def isActiveRefreshable(self) -> bool:

        return self.__refreshIsActive
    
    def activate( self, context:Optional[EvaluationContext]=None, nextRefresh:Optional[TimeInSeconds]=None ) -> None:
        if context is None:
            context = getCurrentEvaluationContext()
        if self.enableDbgOut:  self.dbgOut(f"ActivatablePeriodicRefreshable.activate {self} nextRefresh={nextRefresh}")
        assert self.__autoList is not None, f"ActivatablePeriodicRefreshable {self} has no autoList"
        if nextRefresh is None:
            nextRefresh = self.refreshableCalculateNextRefresh(context, context.when)

        self.__autoList.add( context, self, nextRefresh=nextRefresh ) # type: ignore
        self.__refreshIsActive = True
    
    def deactivate( self, context:Optional[EvaluationContext]=None ) -> None:
        if context is None:
            context = getCurrentEvaluationContext()
        if self.enableDbgOut:  self.dbgOut(f"deactivate")
        assert self.__refreshList is not None
        self.__refreshList.remove( context, self ) # type: ignore
        self.__refreshIsActive = False
        self.__refreshList = None

#############################################################################

class RfMxnActivatablePeriodic(RfMxnActivatable, RfMxnPeriodic):

    class KWDS(RfMxnActivatable.KWDS, RfMxnPeriodic.KWDS):
        pass
        
    #def _mixin_init(self,kwargs:StrAnyDict) -> None:
    #    RfMxnActivatable._mixin_init(self, kwargs)
    #    RfMxnPeriodic._mixin_init(self, kwargs)

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
        kwargs,nliKwds = NamedLocalIdentifiable.extractInitArgs(kwargs)
        NamedLocalIdentifiable.__init__(self, **nliKwds)

#############################################################################

class PeriodicRefreshable( RfMxnPeriodic,Refreshable ):
    RFD_autoRefresh:ClassVar[bool] = True

    class KWDS(Refreshable.KWDS, RfMxnPeriodic.KWDS):
        pass
    
    def __init__(self, **kwargs:Unpack[KWDS] ) -> None:
        #RfMxnPeriodic._mixin_init(self, kwargs)
        Refreshable.__init__(self, mixinKwds=kwargs) # type: ignore[call-arg]


#############################################################################
# pyright: reportPrivateUsage=false

class ActivatablePeriodicRefreshable( RfMxnActivatable, RfMxnPeriodic, Refreshable ):
    RFD_autoRefresh:ClassVar[bool] = True
   
    class KWDS(Refreshable.KWDS, RfMxnActivatable.KWDS, RfMxnPeriodic.KWDS):
        pass

    def __init__(self, **kwargs:Unpack[KWDS] ) -> None:
        #RfMxnActivatable._mixin_init(self, kwargs)
        #RfMxnPeriodic._mixin_init(self, kwargs)
        Refreshable.__init__(self, mixinKwds=kwargs) # type: ignore[call-arg]

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
        Refreshable.__init__(self, mixinKwds=kwargs) # type: ignore[call-arg]

#############################################################################

class RefreshableNAP( RfMxnActivatable, 
                RfMxnPeriodic, 
                RfMxnNamed,
                Refreshable ):

    RFD_autoRefresh:ClassVar[bool] = True
    class KWDS(Refreshable.KWDS, 
               RfMxnNamed.KWDS,
               RfMxnActivatable.KWDS,
               RfMxnPeriodic.KWDS):
        task:NotRequired[Callable[[],None]]

    def __init__(self, **kwds:Unpack[KWDS] ) -> None:
        Refreshable.__init__(self, mixinKwds=kwds) # type: ignore[call-arg]

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

        kwargs,nliKwds = NamedLocalIdentifiable.extractInitArgs(kwargs)
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
    'RefreshableNAP'
]

_sayImport.complete()
