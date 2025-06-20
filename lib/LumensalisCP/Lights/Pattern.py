from .Light import *

import LumensalisCP.Main.Manager

from LumensalisCP.util.bags import Bag

from random import random as randomZeroToOne, randint

#############################################################################

class Pattern(Debuggable):
    
    _theManager:"LumensalisCP.Main.Manager.MainManager" = None
    
    def __init__(self,  target:LightGroup=None, name:str=None, 
                 whenOffset:TimeInSeconds=0.0, startingSpeed:TimeInSeconds=1.0 ):
        self.__name = name or (getattr( target,'name', '') + "-" + self.__class__.__name__)
        super().__init__()
        self.__running = False
        self.__speed:TimeInSeconds = startingSpeed
        assert target is not None
        self.__target = target
        
        self.__whenOffset:TimeInSeconds = whenOffset

    @property
    def whenOffset(self) -> TimeInSeconds : return self.__whenOffset
    
    @whenOffset.setter
    def whenOffset(self,offset:TimeInSeconds): self.__whenOffset = offset
    
    def offsetWhen( self, context:UpdateContext ) -> TimeInSeconds:
        return  context.when + self.__whenOffset
            
    @property
    def name(self) -> str: return self.__name

    @property
    def target(self) -> LightGroup : return  self.__target
    
    @property
    def speed(self) -> TimeInSeconds: return self.__speed
    
    @speed.setter
    def speed(self, value:TimeInSeconds): self.setSpeed(value)
    
    @property
    def running(self) -> bool: return self.__running

    @running.setter
    def running(self, running:bool): self.setRunning(running)

    def setSpeed(self, value:TimeInSeconds, context:UpdateContext|None=None ):
        self.__speed = value

    def setRunning(self, value:bool, context:UpdateContext|None=None ):
        self.__running = value

    def refresh( self, context:UpdateContext ):
        raise NotImplemented

    def main(self):
        if Pattern._theManager is None:
            Pattern._theManager = LumensalisCP.Main.Manager.MainManager.theManager
            assert Pattern._theManager is not None
            
        return Pattern._theManager
    
#############################################################################

class PatternGeneratorStep(object):
    def __init__( self, duration: TimeInSeconds=1.0 ):
        self.duration = duration
    
    def startValue( self, index:int=0, context:UpdateContext = None ): raise NotImplemented
    def endValue( self, index:int=0, context:UpdateContext = None ): raise NotImplemented
    def intermediateValue( self, index:int=0, progression:ZeroToOne = 0, context:UpdateContext = None): raise NotImplemented


#############################################################################

class PatternGeneratorSharedStep(PatternGeneratorStep):
    def __init__( self, 
                 duration: TimeInSeconds=1.0,
                 startValue: AnyLightValue|None =  None, 
                 endValue: AnyLightValue|None =  None, 
                 intermediateRefresh: TimeInSeconds|None = None,
            ):
        super().__init__(duration=duration)
        self._startValue = startValue
        self._endValue = endValue or startValue
        self.duration = duration
        self.intermediateRefresh = intermediateRefresh
    
    @override
    def startValue( self, index:int = 0, context:UpdateContext=None ):
        return context.valueOf( self._startValue )
    
    @override
    def endValue( self, index:int = 0, context:UpdateContext=None ):
        return context.valueOf( self._endValue )

    @override
    def intermediateValue( self, index, progression:ZeroToOne, context:UpdateContext ):
        start = self.startValue(index,context=context)
        return start + ( (self.endValue(index,context=context) - start ) * progression )

#############################################################################

class MultiLightPatternStep(PatternGeneratorSharedStep):
    def __init__(self, duration, starts:List[AnyLightValue], ends:List[AnyLightValue], **kwds ):
        super().__init__(duration=duration, **kwds)
        self.__starts = starts
        self.__ends = ends
    
    @override
    def startValue( self, index:int = 0, context:UpdateContext=None ):
        return context.valueOf( self.__starts[index] )
    
    @override
    def endValue( self, index:int = 0, context:UpdateContext=None ):
        return context.valueOf( self.__ends[index] )

#############################################################################

class PatternGenerator(Pattern):
    def __init__(self, *args, intermediateRefresh:TimeInSeconds|None=None,  **kwargs ):
        super().__init__( *args, **kwargs )
        self.__nextStep = 0.0
        self.__nextRefresh = 0.0
        self.__step:PatternGeneratorSharedStep|None = None
        self.__gen: Generator[PatternGeneratorSharedStep]|None = None
        self.__stepCount = 0
        self.__intermediateCount = 0
    
    def stats(self)->Bag:
        return Bag(
                    nextStep = self.__nextStep, 
                    nextRefresh = self.__nextRefresh, 
                     # = self.__step, 
                    stepCount = self.__stepCount, 
                    intermediateCount = self.__intermediateCount,
        )
        
    def refresh( self, context:UpdateContext ):
        if self.__nextRefresh < context.when:
            if self.__nextStep < context.when:
                self.stepForward( context )
            else:
                when = self.offsetWhen( context )
                duration = context.valueOf(self.__step.duration)
                progression = (self.__nextStep - when) / duration
                self.__nextRefresh = min(  self.__nextStep,
                            when + self.__step.intermediateRefresh )
                self.__intermediateCount += 1
                for lx, light in enumerate(self.target.lights):
                    self.target[lx] = self.__step.intermediateValue(lx,progression,context)
                    #light.setValue( self.__step.intermediateValue(lx,progression,context), context=context )
    
    def stepForward( self, context:UpdateContext ):
        if self.__gen is None:
            self.__gen = self.regenerate( context )
        try:
            self.__step = next(self.__gen)
        except StopIteration:
            self.__gen = self.regenerate( context )
            self.__step = next(self.__gen)

        self.__nextStep = context.when + context.valueOf(self.__step.duration)
        self.__stepCount += 1
        
        if self.__step.intermediateRefresh is not None:
            self.__nextRefresh = context.when + self.__step.intermediateRefresh
        else:
            self.__nextRefresh = self.__nextStep

        for lx, light in enumerate(self.target.lights):
            self.target[lx].set( self.__step.startValue(lx,context) , context )
            #light.setValue( self.__step.startValue(lx,context), context=context )

    def regenerate(self, context:UpdateContext) -> Generator[PatternGeneratorSharedStep]:
        raise NotImplemented

    def setRunning(self, value:bool, context:UpdateContext|None=None ):
        super().setRunning(value, context)

#############################################################################

