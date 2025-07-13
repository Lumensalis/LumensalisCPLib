from LumensalisCP.IOContext import *
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Triggers.Timer import PeriodicTimer
from LumensalisCP.Main.Terms import *
import math

class Oscillator( InputSource ):
    """_summary_
        Provides an input which changes over time in a repeating pattern
    """
    
    frequency:Hertz|Evaluatable 
    low:float|Evaluatable 
    high:float|Evaluatable # destination value
    

    def __init__(self, name:str=None, 
                 frequency:Hertz|Evaluatable = None,
                 period:TimeInSeconds|Evaluatable|None  = None,
                 
                 low:float|Evaluatable = 0.0,
                 high:float|Evaluatable = 1.0,
                 
                **kwds ):
        InputSource.__init__(self, name=name)
        self.low = low
        self.high = high
        if frequency is not None:
            ensure( period is None, "cannot use both frequency and period" )
            self.frequency = frequency
        else:
            if period is not None:
                self.period = period
            else:
                self.frequency = frequency
        
        self._lastFz21 = 0
        self._lastFz21Time:TimeInSeconds = 0.0
        
    @property 
    def period(self) -> float|Evaluatable : return 1.0 / self.frequency
    
    @period.setter
    def period(self, v:float|Evaluatable  ): 
        self.frequency = TERM(1.0) / v
        
    def __recalc( self, context:EvaluationContext ):
        """ move self._lastFz21 from 0.0 to 1.0 (exclusive) at frequency
        
        This uses a time delta instead of simply `divmod( when, frequency )[1]`
        to keep the "signal" consistent when the frequency changes

        :param context: _description_
        :type context: EvaluationContext
        """
        
        now = context.when
        timeDelta = now - self._lastFz21Time
        if timeDelta == 0.0:
            return self._lastFz21
        self._lastFz21Time = now
        frequency = context.valueOf(self.frequency)
        # each cycle takes 1/frequency seconds to go from zero to one
        cycleTime = 1.0 / frequency
        offset = timeDelta / cycleTime
        vOver = offset + self._lastFz21
        v = vOver - math.floor(vOver)
        self.enableDbgOut and self.dbgOut(f"__recalc v={v} prior={self._lastFz21} frequency={frequency} timeDelta={timeDelta:.03f} offset={offset:.03f} vOver={vOver:.03f}")
        self._lastFz21 = v
        return v

    def getDerivedValue(self, context:UpdateContext):
        z2one = self.__recalc(context)
        low = context.valueOf(self.low)
        high = context.valueOf(self.high)
        return low + z2one * (high-low)
    
    
class Sawtooth(Oscillator):
    pass