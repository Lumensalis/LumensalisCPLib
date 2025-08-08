from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( __name__, globals() )

from LumensalisCP.commonPreManager import *

#############################################################################
_sayImport.parsing()

class TimingTracker(NamedLocalIdentifiable):
    """ Tracks timing information for async tasks. """
    
    def __init__(self,**kwds:Unpack[NamedLocalIdentifiable.KWDS]) -> None:
        super().__init__(**kwds)
        self.reset()
        self.__trackGC:bool = False

    @property
    def trackGC(self) -> bool:
        return self.__trackGC
    @trackGC.setter
    def trackGC(self, value: bool) -> None:
        self.__trackGC = value
        self.reset()

    def reset(self) -> None:
        """ Reset the timing tracker. """
        self.loops:int = 0
        self.totalElapsed:TimeSpanInSeconds = 0.0
        self.minElapsed:TimeSpanInSeconds = 9999.0  
        self.maxElapsed:TimeSpanInSeconds = 0.0
        self.zeroElapsed:int = 0
        self.lastReset:TimeInSeconds = getOffsetNow()
        self.startTime:TimeInSeconds|None
        
        self.startMemFree:int = 0
        self.minMemUsed:int|None = None
        self.maxMemUsed:int = 0
        self.totalMemUsed:int = 0

    def start(self, now:Optional[TimeInSeconds]=None) -> TimeInSeconds:
        if self.trackGC:
            self.startMemFree = gc.mem_free()
            if self.enableDbgOut: self.dbgOut( "start memFree=%r", self.startMemFree )
        now = now or getOffsetNow()
        self.startTime = now
            
        return now
    
    def stop(self, now:Optional[TimeInSeconds]=None) -> TimeInSeconds:
        if now is None:
            now = getOffsetNow()
        assert self.startTime is not None, "TimingTracker was not started"
        elapsed = now - self.startTime
        self.addElapsed(elapsed)
        self.startTime = None
        if self.trackGC:
            endMemFree = gc.mem_free()
            memUsed =  self.startMemFree - endMemFree 
            self.totalMemUsed += memUsed
            if self.minMemUsed is None or memUsed < self.minMemUsed:
                self.minMemUsed = memUsed
            if memUsed > self.maxMemUsed:
                self.maxMemUsed = memUsed
            if self.enableDbgOut: self.dbgOut( "stop memUsed=%r", memUsed )
            
        return now  

    def addElapsed(self, elapsed:TimeSpanInSeconds) -> None:
        """ Add elapsed time to the tracker. """
        self.loops += 1
        self.totalElapsed += elapsed
        if elapsed == 0.0:
            self.zeroElapsed += 1
        else:
            self.minElapsed = min(self.minElapsed, elapsed)
            self.maxElapsed = max(self.maxElapsed, elapsed)

    def stats(self, out:Optional[dict[str,Any]]=None) -> dict[str,Any]:
        """ Return stats about the timing tracker. """
        if out is None: out = {}
        
        out['loops'] = self.loops
        loops = self.loops
        if loops > 0:
            clockElapsed = getOffsetNow() - self.lastReset
            out['trackGC'] = self.trackGC
            if self.trackGC:
                out['gc'] = {
                    'avg': self.totalMemUsed / self.loops,
                    'min': self.minMemUsed,
                    'max': self.maxMemUsed,
                    'total': self.totalMemUsed,
                    'start': self.startMemFree
                }
            average = self.totalElapsed / loops
            clockedAverage = clockElapsed / loops
            out['average'] = average
            out['fps'] =  1.0 / average
            out['clocked'] = clockedAverage
            out['cfps'] =  1.0 / clockedAverage
            #out['totalElapsed'] = self.totalElapsed
            #out['clockElapsed'] = clockElapsed
            out['min'] = self.minElapsed
            out['max'] = self.maxElapsed
            out['zeroElapsed'] = self.zeroElapsed


        return out  

#############################################################################
__all__ = ['TimingTracker']
_sayImport.complete()