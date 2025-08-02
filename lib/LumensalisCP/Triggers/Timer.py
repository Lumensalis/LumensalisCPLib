from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayTriggersTimerImport = getImportProfiler("Triggers.Timer" )

from LumensalisCP.IOContext import *

#import LumensalisCP.Main.Manager

#from LumensalisCP.Eval.Expressions import Expression, ExpressionTerm
# pyright: ignore[reportPrivateUsage]

_sayTriggersTimerImport( "Dependents" )

from LumensalisCP.Main.Dependents import SubManagerBase, ManagerRef

_sayTriggersTimerImport( "Trigger")
from LumensalisCP.Triggers.Trigger import Trigger
from LumensalisCP.Triggers.Invocable import *

SimpleCallable:TypeAlias = Callable[[], None]


class PeriodicTimerManager( SubManagerBase ):
    
    def __init__(self, main:MainManager ):
        super().__init__( main=main )
        self.__timers:List["PeriodicTimer"] = []
        self.__timerChanges = 0
        self.__updating = False
        self.__timerSorts = 0
        self.__latestUpdateWhen:TimeInSeconds = TimeInSeconds(0.0)
    
    
    def update(self, context: EvaluationContext ):
        if len(self.__timers) > 0:
            #if self.main.cycle % 10 != 0: return
            self.__updating = True
            now = self.main.when
            self.__latestUpdateWhen = now
            timers = self.__timers
            with context.subFrame('timers.update', self.name ) as activeFrame:
                if self.enableDbgOut: self.dbgOut( "update now=%.3f", now )
                for t in timers:
                    # now = self.main.getNewNow()
                    if t.nextFire is None:
                        continue
                    if t.nextFire <= now:
                        priorNf = t.nextFire
                        try:
                            t._timerExpired( now, context=context ) # pyright: ignore[reportPrivateUsage] # pylint: disable=protected-access
                        except Exception as inst: # pylint: disable=broad-except
                            t.SHOW_EXCEPTION( inst, "timer expire exception" )
                        #self.enableDbgOut and 
                        if self.enableDbgOut: self.dbgOut( f"timer {t.name} expired, nf={t.nextFire} now={now:.3f} pnf={priorNf}" )
                    else:
                        #self.enableDbgOut and 
                        if self.enableDbgOut: self.dbgOut( "timer %s still waiting, nf=%0.3f", t.name, t.nextFire )
                                        
                self.__updating = False
                if self.__timerChanges:
                    activeFrame.snap( "__shuffleTimers" )
                    if self.enableDbgOut: self.dbgOut( "%d changes, shuffling", self.__timerChanges )
                    self.__shuffleTimers(context)

    def derivedRefresh(self,context:'EvaluationContext') -> None:
        self.update(context)
    
    @property
    def timers(self) -> List[PeriodicTimer]: return self.__timers
    
    def __shuffleTimers( self, context:Optional[EvaluationContext]=None ) -> None:
        if context is None: context = getCurrentEvaluationContext()
        if self.__updating:
            self.__timerChanges += 1
        else:
            self.__timerChanges = 0
            #self.__timers = sorted( filter( lambda t: t.nextFire is not None, self.__timers ), key=lambda t: t.nextFire )
            self.__timers.sort( key=lambda t: t.nextFire or self.__latestUpdateWhen + 9999  )
            
            self.__timerSorts += 1
            if len(self.__timers) > 0:
                nextFire = self.__timers[0].nextFire 
                assert nextFire is not None
                self.setNextRefresh( context, nextFire )
                if not self.isActiveRefreshable: self.activate(context)
            else:
                if self.isActiveRefreshable: self.deactivate(context)

    @property
    def timerSorts(self) -> int: return self.__timerSorts
    
    def _addTimer( self, timer:"PeriodicTimer" ) -> None:
        assert timer not in self.__timers
        self.__timers.append( timer )
        self.__shuffleTimers()

    def _updateTimer( self, timer:"PeriodicTimer" ) -> None:
        assert timer in self.__timers
        self.__shuffleTimers()
            
    def _removeTimer( self, timer:"PeriodicTimer" ) -> None:
        assert timer in self.__timers
        self.__timers.remove( timer )
        self.__shuffleTimers()
        
        
class PeriodicTimer( Trigger ):
    # pylint: disable=protected-access
    IntervalArg:TypeAlias = Union[TimeSpanInSeconds,Callable[[],TimeSpanInSeconds]]
    
    class KWDS(Trigger.KWDS):
        interval: NotRequired[Union[TimeSpanInSeconds,Callable[[],TimeSpanInSeconds]]]
        oneShot: NotRequired[bool]
        manager: NotRequired[PeriodicTimerManager]

    def __init__(self, 
                    interval:IntervalArg = 1.0,
                    oneShot:bool = False,
                    manager:Optional[PeriodicTimerManager] = None,
                    **kwds:Unpack[Trigger.KWDS]
            ) -> None:
        super().__init__(**kwds)
        self.__interval:PeriodicTimer.IntervalArg = interval
        self.__lastFire:TimeInSeconds = TimeInSeconds(0.0)
        self.__nextFire:TimeInSeconds|None = None
        self.__oneShot:bool = oneShot
        if manager is None:
            manager = getMainManager().timers
        self.__managerRef = ManagerRef(manager)

    @property
    def manager(self) -> PeriodicTimerManager: 
        return self.__managerRef() # type: ignore

    @property
    def running(self) -> bool: return self.__nextFire is not None

    @property
    def lastFire(self) -> TimeInSeconds: return self.__lastFire
    
    @property
    def nextFire(self) -> TimeInSeconds|None:
        return self.__nextFire
    
    def getInterval(self) -> TimeSpanInSeconds:
        i = self.__interval
        if isinstance(i,(float,int)):
            return float(i)
        i = i()
        assert isinstance( i, float )
        return i
        
    @property
    def interval(self) -> TimeSpanInSeconds: return self.getInterval()

    
    @interval.setter
    def interval(self,interval:TimeSpanInSeconds|Callable[[],TimeSpanInSeconds]) -> None:
        self.__interval = interval
        if self.running:
            self.start()
    
    @final
    def start(self, interval:TimeSpanInSeconds|None =None ):
        """start or restart the time"""
        interval = interval or self.getInterval()
        self.startupOut( f"start {self.name} when = {self.manager.main.when} interval={interval} _nextFire={self.__nextFire}" )
        nextFire = self.manager.main.when + interval 
        if self.__nextFire is None:
            self.__nextFire = nextFire # type: ignore
            self.manager._addTimer(self) # pyright: ignore[reportPrivateUsage]
        else:
            self.__nextFire = nextFire # type: ignore
            self.manager._updateTimer(self) # pyright: ignore[reportPrivateUsage]
    
    @final
    def stop(self):
        if self.__nextFire is not None:
            self.__nextFire = None
            self.manager._removeTimer( self ) # pyright: ignore[reportPrivateUsage]
    
    @final
    def restart(self, interval:TimeSpanInSeconds|Callable[...,TimeSpanInSeconds]|None =None, when:TimeInSeconds|None = None ):
        """restart the timer"""
        assert self.__nextFire is not None
        when = when or self.manager.main.when
        if interval is not None:
            self.__interval = interval
        interval = self.getInterval()
        self.__nextFire = when + interval # type: ignore
        if self.enableDbgOut: self.dbgOut( "restart at %.3fs i=%.3fs nf=%.3fs", when, interval, self.__nextFire)
        #self._nextFire = min( when, self._nextFire + self.__interval )
        self.manager._updateTimer(self) # pyright: ignore[reportPrivateUsage]


    def addSimpleTaskDef( self, name:Optional[str]=None, autoStart:bool=True) -> Callable[[InvocableOrSimpleCB], Invocable]:
        def wrapper( cb:InvocableOrSimpleCB  ) -> Invocable:
            invocable = InvocableSimpleCB.make(cb)
            self.addAction( invocable )
            if autoStart:
                self.start()
            return invocable

        return wrapper
    
    #########################################################################
    # ONLY FOR USE BY PeriodicTimerManager
    def _timerExpired(self, when:TimeInSeconds, context: EvaluationContext ) -> None:
        
        #self.fire(when=when, context=context)
        with context.subFrame('_timerExpired', self.name ) as activeFrame:
            self.fireTrigger( context=context )
            self.__lastFire = when
            if self.__oneShot:
                activeFrame.snap( "stop" )
                self.stop()
            else:
                if self.__nextFire is not None:
                    activeFrame.snap( "restart" )
                    self.restart(when=when)

def addPeriodicTaskDef( **kwargs:Unpack[PeriodicTimer.KWDS]
        )   -> Callable[[InvocableOrContextCB], PeriodicTimer]:
#Callable[[InvocableOrContextCB], PeriodicTimer]:

    def wrapper( cb:InvocableOrContextCB  ) -> PeriodicTimer:
        m = kwargs.get("main") or getMainManager()
        kwargs.setdefault('manager', m.timers )
        #kwCb = KWCallback(cb,name=name)
        timer = PeriodicTimer( **kwargs )
        invocable = Invocable.makeInvocable(cb)
        timer.addAction( invocable )
        timer.start()
        return timer

    return wrapper


def addSimplePeriodicTaskDef( **kwds:Unpack[PeriodicTimer.KWDS]
        ) -> Callable[[InvocableOrSimpleCB], Invocable]:

    def wrapper( cb:InvocableOrSimpleCB  ) -> Invocable:
        timer = PeriodicTimer( **kwds )
        invocable = InvocableSimpleCB.make(cb)
        timer.addRawAction( invocable )
        timer.start()
        return invocable

    return wrapper

_sayTriggersTimerImport.complete(globals())
