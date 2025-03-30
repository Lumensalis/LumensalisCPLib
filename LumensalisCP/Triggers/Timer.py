from LumensalisCP.common import *
from LumensalisCP.CPTyping import *

import LumensalisCP.Main.Manager

from LumensalisCP.Main.Expressions import InputSource, UpdateContext
from  LumensalisCP.Main.Dependents import SubManagerBase, ManagerRef
from . import Trigger

class PeriodicTimerManager( SubManagerBase ):
    
    def __init__(self, main:"LumensalisCP.Main.Manager.MainManager" ):
        super().__init__( main=main )
        self.__timers:List["PeriodicTimer"] = []
        self.__timerChanges = 0
        self.__updating = False
    
    def update(self, context: UpdateContext ):
        if len(self.__timers):
            self.__updating = True
            now = self.main.when
            timers = self.__timers
            self.dbgOut( "update now=%.3f", now )
            for t in timers:
                now = self.main.newNow
                if t._nextFire <= now:
                    priorNf = t._nextFire
                    t._timerExpired( now, context=context )
                    self.dbgOutEnabled and self.dbgOut( f"timer {t.name} expired, nf={t._nextFire:0.3f} now={now:.3f} pnf={priorNf:.3f}" )
                else:
                    self.dbgOutEnabled and self.dbgOut( f"timer {t.name} still waiting, nf={t._nextFire:0.3f}" )
                                    
            self.__updating = False
            if self.__timerChanges:
                self.dbgOut( "%d changes, shuffling", self.__timerChanges )
                self.__shuffleTimers()

    def __shuffleTimers( self ):
        if self.__updating:
            self.__timerChanges += 1
        else:
            self.__timerChanges = 0
            self.__timers = sorted( filter( lambda t: t._nextFire is not None, self.__timers ) )

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
    
    def __init__(self, interval:TimeInSeconds=1.0, name:str = None, oneShot:bool = False, manager:PeriodicTimerManager = None ):
        super().__init__(name=name)
        self.__interval:TimeInSeconds = interval
        self.__lastFire:TimeInSeconds = 0.0
        self._nextFire:TimeInSeconds|None = None
        self.__oneShot:bool = oneShot
        self.__managerRef = ManagerRef(manager)

    @property
    def manager(self) -> PeriodicTimerManager: return self.__managerRef()

    @property
    def running(self) -> bool: return self._nextFire is not None

    @property
    def lastFire(self) -> TimeInSeconds: return self.__lastFire
    
    @property
    def interval(self) -> TimeInSeconds: return self.__interval

    
    @interval.setter
    def interval(self,interval:TimeInSeconds):
        self.__interval = interval
        if self.running:
            self.start()
    
    @final
    def start(self, interval:float|None =None ):
        """start or restart the time"""
        interval = interval or self.__interval    
        next = self.manager.main.when + interval 
        if self._nextFire is None:
            self._nextFire = next
            self.manager._addTimer(self)
        else:
            self._nextFire = next
            self.manager._updateTimer(self)
    
    @final
    def stop(self):
        if self._nextFire is not None:
            self._nextFire = None
            self.manager._removeTimer( self )
    
    @final
    def restart(self, interval:float|None =None, when:TimeInSeconds|None = None ):
        """restart the timer"""
        assert self._nextFire is not None
        when = when or self.manager.main.when
        if interval is not None:
            self.__interval = interval
        self._nextFire = when + self.__interval
        self.dbgOut and self.dbgOut( "restart at %.3fs i=%.3fs nf=%.3fs", when, self.__interval, self._nextFire)
        #self._nextFire = min( when, self._nextFire + self.__interval )
        self.manager._updateTimer(self)

    #########################################################################
    # ONLY FOR USE BY PeriodicTimerManager
    def _timerExpired(self, when:float, context: UpdateContext = None):
        
        self.fire(when=when, context=context)
        self.__lastFire = when
        if self.__oneShot:
            self.stop()
        else:
            if self._nextFire is not None:
                self.restart(when=when)


