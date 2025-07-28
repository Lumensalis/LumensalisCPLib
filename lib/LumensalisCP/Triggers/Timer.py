from __future__ import annotations
from typing import List

from LumensalisCP.Main.PreMainConfig import ImportProfiler
_sayTriggersTimerImport = ImportProfiler("Triggers.Timer" )

from LumensalisCP.IOContext import *

#import LumensalisCP.Main.Manager

#from LumensalisCP.Eval.Expressions import Expression, ExpressionTerm
_sayTriggersTimerImport( "Dependents" )

from LumensalisCP.Main.Dependents import SubManagerBase, ManagerRef

_sayTriggersTimerImport( "Trigger")
from LumensalisCP.Triggers.common import Trigger
    
    
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
            if self.enableDbgOut: self.dbgOut( "update now=%.3f", now )
            for t in timers:
                # now = self.main.getNewNow()
                if t.nextFire is None:
                    continue
                if t.nextFire <= now:
                    priorNf = t.nextFire
                    try:
                        t._timerExpired( now, context=context ) # pylint: disable=protected-access
                    except Exception as inst: # pylint: disable=broad-except
                        t.SHOW_EXCEPTION( inst, "timer expire exception" )
                    #self.enableDbgOut and 
                    if self.enableDbgOut: self.dbgOut( f"timer {t.name} expired, nf={t.nextFire} now={now:.3f} pnf={priorNf}" )
                else:
                    #self.enableDbgOut and 
                    if self.enableDbgOut: self.dbgOut( "timer %s still waiting, nf=%0.3f", t.name, t.nextFire )
                                    
            self.__updating = False
            if self.__timerChanges:
                if self.enableDbgOut: self.dbgOut( "%d changes, shuffling", self.__timerChanges )
                self.__shuffleTimers()

    @property
    def timers(self) -> List[PeriodicTimer]: return self.__timers
    
    def __shuffleTimers( self ):
        if self.__updating:
            self.__timerChanges += 1
        else:
            self.__timerChanges = 0
            #self.__timers = sorted( filter( lambda t: t.nextFire is not None, self.__timers ), key=lambda t: t.nextFire )
            self.__timers.sort( key=lambda t: t.nextFire or self.__latestUpdateWhen + 9999  )
            
            self.__timerSorts += 1

    @property
    def timerSorts(self) -> int: return self.__timerSorts
    
    def _addTimer( self, timer:"PeriodicTimer" ):
        assert timer not in self.__timers
        self.__timers.append( timer )
        self.__shuffleTimers()

    def _updateTimer( self, timer:"PeriodicTimer" ):
        assert timer in self.__timers
        self.__shuffleTimers()
            
    def _removeTimer( self, timer:"PeriodicTimer" ):
        assert timer in self.__timers
        self.__timers.remove( timer )
        self.__shuffleTimers()
        
        
class PeriodicTimer( Trigger ):
    # pylint: disable=protected-access
    
    def __init__(self, interval:TimeSpanInSeconds=1.0, name:Optional[str] = None, oneShot:bool = False, manager:Optional[PeriodicTimerManager] = None ):
        super().__init__(name=name)
        self.__interval:TimeSpanInSeconds|Callable = interval
        self.__lastFire:TimeInSeconds = TimeInSeconds(0.0)
        self.__nextFire:TimeInSeconds|None = None
        self.__oneShot:bool = oneShot
        assert manager is not None
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
        if isinstance(i,(float,int)):
            return float(i)

        assert isinstance( i, float )
        return i
        
    @property
    def interval(self) -> TimeSpanInSeconds: return self.getInterval()

    
    @interval.setter
    def interval(self,interval:TimeSpanInSeconds|Callable):
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
            self.manager._addTimer(self)
        else:
            self.__nextFire = nextFire # type: ignore
            self.manager._updateTimer(self)
    
    @final
    def stop(self):
        if self.__nextFire is not None:
            self.__nextFire = None
            self.manager._removeTimer( self )
    
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
        self.manager._updateTimer(self)


    def addTaskDef( self, name:Optional[str]=None, autoStart=True):
        def wrapper( cb:Callable[...,Any]  ) -> KWCallback:
            wrapped = KWCallback.make(cb,name=name)
            self.addAction( wrapped )
            if autoStart:
                self.start()
            return wrapped

        return wrapper
    
    #########################################################################
    # ONLY FOR USE BY PeriodicTimerManager
    def _timerExpired(self, when:TimeInSeconds, context: EvaluationContext ):
        
        self.fire(when=when, context=context)
        self.__lastFire = when
        if self.__oneShot:
            self.stop()
        else:
            if self.__nextFire is not None:
                self.restart(when=when)

def addPeriodicTaskDef( name:Optional[str]=None, period:TimeSpanInSeconds=1.1,main:Optional[MainManager]=None):
    def wrapper( cb:Callable[...,Any]  ) -> KWCallback:
        
        m = main or getMainManager()
        kwCb = KWCallback(cb,name=name)
        timer = PeriodicTimer( period, manager=m.timers, name=name,)
        timer.addAction( kwCb )
        timer.start()
        return kwCb

    return wrapper

_sayTriggersTimerImport.complete()
