from __future__ import annotations

import math

from LumensalisCP.IOContext import *
from LumensalisCP.Eval.Terms import *
#from LumensalisCP.Main.Manager import MainManager
#from LumensalisCP.Triggers.Timer import PeriodicTimer
#from lumensaliscplib.lib.LumensalisCP import Eval
from LumensalisCP.Temporal.Refreshable import Refreshable, RfMxnActivatablePeriodic

class EvalDescriptorHolder:
    def onDescriptorSet(self, name:str, value:Evaluatable[Any]|EVAL_VALUE_TYPES) -> Any:
        """Called when a descriptor is set on this object"""
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement onDescriptorSet")
        
_EDT = TypeVar('_EDT' )

class EvalDescriptorMetaclass(type):
    pass
    def __getitem__(cls, v:Any) -> Any:
        """Get an EvalDescriptor for the given name"""
        return v

class EvalDescriptor(Generic[_EDT]):
    def __init__(self, name:str, default:_EDT|None = None):
        self.name = name
        self.attrName = f"_d_{name}"
        self.default = default
        
        
    def __get__(self, instance:EvalDescriptorHolder, owner:Any=None) -> _EDT|Evaluatable[_EDT]:
        rv = getattr( instance, self.attrName,None )
        if rv is None: rv = self.default
        return rv # type: ignore
    
    def __set__(self, instance:EvalDescriptorHolder, value:_EDT|Evaluatable[_EDT]) -> None:
        assert instance is not None,  f"Cannot set {self.name} "
        setattr( instance, self.attrName, value )
        instance.onDescriptorSet(self.name, value)

class Oscillator( InputSource, EvalDescriptorHolder, RfMxnActivatablePeriodic, Refreshable ):
    """_summary_
        Provides an input which changes over time in a repeating pattern
    """
    RFD_refreshRate:ClassVar[TimeSpanInSeconds] = 0.05
    RFD_autoRefresh:ClassVar[bool] = True

    class KWDS( InputSource.KWDS, RfMxnActivatablePeriodic.KWDS, Refreshable.KWDS ):
        frequency: NotRequired[Hertz|Evaluatable[Hertz]]
        period: NotRequired[TimeInSeconds]
        low: NotRequired[float|Evaluatable[float]]
        high: NotRequired[float|Evaluatable[float]]
        
    frequency:EvalDescriptor[Hertz]=EvalDescriptor('frequency', 1.0)
    low:EvalDescriptor[float]=EvalDescriptor('low', 0.0)
    high:EvalDescriptor[float]=EvalDescriptor('high', 1.0)

    def __init__(self, **kwds:Unpack[KWDS] ) -> None:
        main = kwds.get('main', getMainManager())
        kwds.setdefault('autoList', main.refreshables)
        frequency = kwds.pop('frequency', None)
        period = kwds.pop('period', None)
        low = kwds.pop('low', 0.0)
        high = kwds.pop('high', 1.0)
        Refreshable.__init__(self, mixinKwds=kwds )

        InputSource.__init__( self, **kwds )

        self.low = low
        self.high = high
        if frequency is None:
            assert period is not None, "cannot use both frequency and period"
            frequency = period
        else:
            assert period is None, "cannot use both frequency and period"
        
        self.frequency = frequency
        
        self._lastFz21 = 0
        self._lastFz21Time:TimeInSeconds = TimeInSeconds(0.0)
        
    def onDescriptorSet(self, name:str, value:Evaluatable[Any]|EVAL_VALUE_TYPES) -> None:
        """Called when a descriptor is set on this object"""

    def derivedRefresh(self, context:EvaluationContext) -> None:
        if self.enableDbgOut:
            self.dbgOut(f"derivedRefresh called for {self.__class__.__name__} at {context.when} with frequency={self.frequency}, low={self.low}, high={self.high}")
        self.updateValue(context)
        
    @property
    def period(self) -> TimeInSeconds:
        f = evaluate(self.frequency) # type: ignore
        return 1.0 / f # type: ignore

    @period.setter
    def period(self, v:float|Evaluatable[float]  ): 
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
        if self.enableDbgOut: self.dbgOut(f"__recalc v={v} prior={self._lastFz21} frequency={frequency} timeDelta={timeDelta:.03f} offset={offset:.03f} vOver={vOver:.03f}")
        self._lastFz21 = v
        return v

    def getDerivedValue(self, context:EvaluationContext):
        z2one = self.__recalc(context)
        low = context.valueOf(self.low)
        high = context.valueOf(self.high)
        return low + z2one * (high-low)
    
    
class Sawtooth(Oscillator):
    pass
