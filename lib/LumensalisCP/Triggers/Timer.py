from LumensalisCP.IOContext import *

import LumensalisCP.Main.Manager

from LumensalisCP.Main.Expressions import Expression, ExpressionTerm
from  LumensalisCP.Main.Dependents import SubManagerBase, ManagerRef
from . import Trigger
from LumensalisCP.util.kwCallback import KWCallback

class PeriodicTimerManager( SubManagerBase ):
    
    def __init__(self, main:"LumensalisCP.Main.Manager.MainManager" ):
        super().__init__( main=main )
        self.__timers:List["PeriodicTimer"] = []
        self.__timerChanges = 0
        self.__updating = False
        self.__timerSorts = 0
        
    def update(self, context: UpdateContext ):
        if len(self.__timers):
            #if self.main.cycle % 10 != 0: return
            self.__updating = True
            now = self.main.when
            self.__latestUpdateWhen = now
            timers = self.__timers
            if self.enableDbgOut: self.dbgOut( "update now=%.3f", now )
            for t in timers:
                now = self.main.newNow
                if t.nextFire is None:
                    pass
                if t.nextFire <= now:
                    priorNf = t.nextFire
                    try:
                        t._timerExpired( now, context=context )
                    except Exception as inst:
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
    def timers(self): return self.__timers
    
    def __shuffleTimers( self ):
        if self.__updating:
            self.__timerChanges += 1
        else:
            self.__timerChanges = 0
            #self.__timers = sorted( filter( lambda t: t.nextFire is not None, self.__timers ), key=lambda t: t.nextFire )
            self.__timers.sort( key=lambda t: t.nextFire or self.__latestUpdateWhen + 9999  )
            
            self.__timerSorts += 1

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
    
    def __init__(self, interval:TimeSpanInSeconds=1.0, name:str = None, oneShot:bool = False, manager:PeriodicTimerManager = None ):
        super().__init__(name=name)
        self.__interval:TimeSpanInSeconds|Callable = interval
        self.__lastFire:TimeInSeconds = 0.0
        self.__nextFire:TimeInSeconds|None = None
        self.__oneShot:bool = oneShot
        self.__managerRef = ManagerRef(manager)

    @property
    def manager(self) -> PeriodicTimerManager: return self.__managerRef()

    @property
    def running(self) -> bool: return self.__nextFire is not None

    @property
    def lastFire(self) -> TimeInSeconds: return self.__lastFire
    
    @property
    def nextFire(self) -> TimeInSeconds: return self.__nextFire
    
    def getInterval(self) -> TimeSpanInSeconds:
        i = self.__interval
        if type(i) is float: return i
        if type(i) is int:  return float(i)
        
        i = i()
        if type(i) is float: return i
        if type(i) is int:  return float(i)

        ensure( type(i) is float )
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
        print( f"start {self.name} when = {self.manager.main.when} interval={interval} _nextFire={self.__nextFire}" )
        next = self.manager.main.when + interval 
        if self.__nextFire is None:
            self.__nextFire = next
            self.manager._addTimer(self)
        else:
            self.__nextFire = next
            self.manager._updateTimer(self)
    
    @final
    def stop(self):
        if self.__nextFire is not None:
            self.__nextFire = None
            self.manager._removeTimer( self )
    
    @final
    def restart(self, interval:TimeSpanInSeconds|Callable|None =None, when:TimeInSeconds|None = None ):
        """restart the timer"""
        assert self.__nextFire is not None
        when = when or self.manager.main.when
        if interval is not None:
            self.__interval = interval
        interval = self.getInterval()
        self.__nextFire = when + interval
        if self.enableDbgOut: self.dbgOut and self.dbgOut( "restart at %.3fs i=%.3fs nf=%.3fs", when, interval, self.__nextFire)
        #self._nextFire = min( when, self._nextFire + self.__interval )
        self.manager._updateTimer(self)

    def addTaskDef( self, name:str|None=None, autoStart=True):
        def wrapper( callable:Callable  ):
            cb = KWCallback.make(callable,name=name)
            self.addAction( cb )
            if autoStart:
                self.start()
            return cb

        return wrapper
    #########################################################################
    # ONLY FOR USE BY PeriodicTimerManager
    def _timerExpired(self, when:float, context: UpdateContext = None):
        
        self.fire(when=when, context=context)
        self.__lastFire = when
        if self.__oneShot:
            self.stop()
        else:
            if self.__nextFire is not None:
                self.restart(when=when)

def addPeriodicTaskDef( name:str|None=None, period:TimeSpanInSeconds=1.1,main:LumensalisCP.Main.Manager.MainManager|None = None):
    def wrapper( callable:Callable  ):
        
        cb = KWCallback(callable,name=name)
        timer = PeriodicTimer( period, manager=main.timers, name=name,)
        timer.addAction( cb )
        timer.start()
        return cb

    return wrapper