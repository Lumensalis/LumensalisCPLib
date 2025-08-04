from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( __name__, globals() )

from LumensalisCP.commonPreManager import *

#############################################################################
_sayImport.parsing()

class TimingTracker(CountedInstance):
    """ Tracks timing information for async tasks. """
    
    def __init__(self):
        super().__init__()
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

    def start(self, now:Optional[TimeInSeconds]=None) -> TimeInSeconds:
        now = now or getOffsetNow()
        self.startTime = now
        return now
    def stop(self) -> TimeSpanInSeconds:
        now = getOffsetNow()
        assert self.startTime is not None, "TimingTracker was not started"
        elapsed = now - self.startTime
        self.addElapsed(elapsed)
        self.startTime = None
        return elapsed  

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