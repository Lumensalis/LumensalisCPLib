from __future__ import annotations

from LumensalisCP.Lights._common import *

#############################################################################

def prepRGBValue( value:RGBEvalArg ) -> RGBEval:
    
    if (
            isinstance( value, Evaluatable ) or
            callable(value)
    ):
        return value # type: ignore
    return RGB.toRGB( value ) # type: ignore

#############################################################################
class Rainbow( Pattern ):
    """A rainbow color pattern.
    """
    def __init__(self,
                 target:LightGroup,
                 colorCycle:TimeInSecondsEvalArg = 1.0,
                 spread:float|Evaluatable[float] = 1,
                 **kwargs:Unpack[Pattern.KWDS]
            ):
        self.__colorCycle:TimeInSecondsEval = toTimeInSecondsEval(colorCycle)
        self.__colorCycleWhenOffset:TimeInSeconds = TimeInSeconds(0.0)
        self.__latestCycleWhen = 0
        self.spread = spread
        super().__init__(target, **kwargs)

    @property
    def colorCycle(self): 
        return self.__colorCycle
    
    @colorCycle.setter
    def colorCycle( self, newCycle:TimeInSecondsEvalArg ):
        priorOffset = self.__colorCycleWhenOffset
        priorCycle = self.__latestCycleValue
        newWhen = priorWhen = self.__latestCycleWhen
        '''
        A = ((priorWhen+priorOffset) / priorCycle)
        B = ((newOffset+newWhen) / newCycle)
        
        ((newOffset+newWhen) / newCycle) = ((priorWhen+priorOffset) / priorCycle) 
        newOffset+newWhen = ((priorWhen+priorOffset) / priorCycle) * newCycle
        newOffset = (((priorWhen+priorOffset) / priorCycle) * newCycle) - newWhen
        '''
        newCycleSetting = toTimeInSecondsEval(newCycle)
        if isinstance(newCycleSetting, float):
            newCycleCurrent = newCycleSetting
        else:
            newCycleCurrent = UpdateContext.fetchCurrentContext(None).valueOf(newCycleSetting)
        self.__colorCycleWhenOffset = TimeInSeconds( (((priorWhen+priorOffset) / priorCycle) * newCycleCurrent) - newWhen)
        self.__colorCycle = newCycleSetting
    
    def patternRefresh( self, context:EvaluationContext ):
        when = self.offsetWhen( context )
        self.__latestCycleWhen = when
        cc = max(0.001,context.valueOf(self.colorCycle))
        self.__latestCycleValue = cc
        #print( f"cc = {cc} from {self.colorCycle}")
        A = (when + self.__colorCycleWhenOffset) / cc
        ensure( type(A) is float, f"A is {type(A)}, not float" )
        
        target = self.target
        spread = context.valueOf(self.spread)
        if spread == 0:
            pxStep = 0
        else:
            pxStep = 1 / (target.lightCount * context.valueOf(spread) )
            
        # set each pixel
        for px in range(target.lightCount):
            target[px] = wheel1( A + (px * pxStep) )

#############################################################################
class Gauge( OnOffPattern, NamedOutputTarget ):

    class KWDS(OnOffPattern.KWDS,NamedOutputTarget.KWDS):
        pass
    
    def __init__(self,
                target:LightGroup, 
                value:ZeroToOne|Evaluatable[ZeroToOne] = 0.0,
                **kwargs:Unpack[OnOffPattern.KWDS]
            ):
        self.__value = value

        kwargs, notArgs = NamedOutputTarget.extractInitArgs(kwargs)
        NamedOutputTarget.__init__(self, **notArgs )
        OnOffPattern.__init__( self, target , **kwargs)
        self._mix = RGB(Colors.BLACK)

    @property
    def value(self)->ZeroToOne|Evaluatable[ZeroToOne]: return self.__value

    def set( self, value:ZeroToOne, context:EvaluationContext ):
        self.__value = value

    def patternRefresh( self, context:EvaluationContext ):
        level = withinZeroToOne( context.valueOf(self.__value) )
        target = self.target
        maxPxf = level * target.lightCount
        maxPx = int(maxPxf)
        pxR = maxPxf - maxPx
        
        onValue = RGB.toRGB( context.valueOf( self._onValue) )
        offValue = RGB.toRGB( context.valueOf(self._offValue) )
        
        
        for px in range(target.lightCount):
            if px < maxPx:
                v = onValue 
            elif px > maxPx:
                v = offValue 
            else:
                self._mix.fadeAB(offValue, onValue, pxR)
                v = self._mix
                if self.enableDbgOut:
                    self.dbgOut(f" px={px}, v={v}, offValue={offValue}, onValue={onValue},  pxR = {pxR}")
            target[px] = v # type: ignore[assignment]

#############################################################################

class Blink( OnOffPattern ):
    def __init__(self,
                target:LightGroup, 
                 onTime:TimeInSecondsEvalArg = 1.0,
                 offTime:TimeInSecondsEvalArg = 1.0,
                 **kwargs:Unpack[OnOffPattern.KWDS]
            ) -> None:
        self.onTime = onTime
        self.offTime = offTime
        self.lastToggleTime:TimeInSeconds = TimeInSeconds(0.0)
        self.lastToggleValue:bool = False

        super().__init__(target,**kwargs)
        


    def patternRefresh( self, context:EvaluationContext ):
        if self.lastToggleValue:
            duration = context.valueOf(self.onTime)
        else:
            duration = context.valueOf(self.offTime)

        if context.when <= self.lastToggleTime + duration:
            return
    
        self.lastToggleTime = context.when
        self.lastToggleValue = not self.lastToggleValue

        if self.lastToggleValue: value = self.getOnValue(context)
        else: value = self.getOffValue(context)    
        
        for led in self.target:
            led.set(value,context)

#############################################################################

#############################################################################

#############################################################################

__all__ = ['Rainbow','Gauge','Blink','prepRGBValue']