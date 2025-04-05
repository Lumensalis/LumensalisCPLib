from .LightBase import *

#############################################################################

class Pattern(Debuggable):
    def __init__(self,  target:LightGroupBase=None, name:str=None, 
                 whenOffset:TimeInSeconds=0.0, startingSpeed:TimeInSeconds=1.0 ):
        self.__name = name or (getattr( target,'name', '') + "-" + self.__class__.__name__)
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
    def target(self) -> LightGroupBase : return  self.__target
    
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


#############################################################################
class Rainbow( Pattern ):
    def __init__(self,
                 *args,
                 colorCycle:TimeInSeconds = 1.0,
                 spread:float = 1,
                 **kwargs
            ):
        self.colorCycle = colorCycle
        self.spread = spread
        super().__init__(*args,**kwargs)
        
    def refresh( self, context:UpdateContext ):
        when = self.offsetWhen( context )
        A = when  / context.valueOf( self.colorCycle)
        target = self.target
        pxStep = 1 / (target.lightCount * context.valueOf(self.spread) )
        # set each pixel
        for px in range(target.lightCount):
            target[px] = wheel1( A + (px * pxStep) )
            
        #blinker.refresh( main.latestContext )
            


#############################################################################
class PatternGeneratorStep(object):
    def __init__( self, duration: TimeInSeconds=1.0 ):
        self.duration = duration
    
    def startValue( self, index, context:UpdateContext ): raise NotImplemented
    def endValue( self, index, context:UpdateContext ): raise NotImplemented
    def intermediateValue( self, index, progression:ZeroToOne, context:UpdateContext ): raise NotImplemented

#############################################################################

class PatternGeneratorSharedStep(PatternGeneratorStep):
    def __init__( self, 
                 duration: TimeInSeconds,
                 startValue: AnyLightValue, 
                 endValue: AnyLightValue|None =  None, 
                 intermediateRefresh: TimeInSeconds|None = None,
            ):
        super().__init__(duration=duration)
        self._startValue = startValue
        self._endValue = endValue
        self.duration = duration
        self.intermediateRefresh = intermediateRefresh
    
    def startValue( self, index, context:UpdateContext ):
        return self._startValue
    
    def endValue( self, index, context:UpdateContext ):
        return self._endValue

    def intermediateValue( self, index, progression:ZeroToOne, context:UpdateContext ):
        return self._startValue + (self._endValue - self._startValue) * progression

#############################################################################

#############################################################################

class PatternGenerator(Pattern):
    def __init__(self, *args,  **kwargs ):
        super().__init__( *args, **kwargs )
        self.__nextStep = 0.0
        self.__nextRefresh = 0.0
        self.__step:PatternGeneratorStep|None = None
        self.__gen: Generator[PatternGeneratorStep]|None = None
    
    def refresh( self, context:UpdateContext ):
        if self.__nextRefresh < context.when:
            if self.__nextStep < context.when:
                self.stepForward( context )
            else:
                when = self.offsetWhen( context )
                progression = (self.__nextStep - when) / self.__step.duration
                self.__nextRefresh = min(  self.__nextStep,
                            when + self.__step.intermediateRefresh )
                for lx, light in enumerate(self.target.lights):
                    light.setValue( self.__step.intermediateValue(lx,progression,context), context=context )

    def stepForward( self, context:UpdateContext ):
        if self.__gen is None:
            self.__gen = self.regenerate( context )
        try:
            self.__step = next(self.__gen)
        except StopIteration:
            self.__gen = self.regenerate( context )
            self.__step = next(self.__gen)

        self.__nextStep = context.when + self.__step.duration
        
        if self.__step.intermediateRefresh is not None:
            self.__nextRefresh = context.when + self.__step.intermediateRefresh
        else:
            self.__nextRefresh = self.__nextStep

        for lx, light in enumerate(self.target.lights):
            light.setValue( self.__step.startValue(lx,context), context=context )

    def regenerate(self, context:UpdateContext) -> Generator[PatternGeneratorStep]:
        raise NotImplemented

    def setRunning(self, value:bool, context:UpdateContext|None=None ):
        super().setRunning(value, context)

#############################################################################

class Blink( PatternGenerator ):
    def __init__(self,
                 *args,
                 onTime:TimeInSeconds = 1.0,
                 offTime:TimeInSeconds = 1.0,
                 onValue:AnyLightValue = 1.0,
                 offValue:AnyLightValue = 0.0,
                 **kwargs
            ):
        self.onTime = onTime
        self.offTime = offTime
        self.onValue = onValue
        self.offValue = offValue
        super().__init__(*args,**kwargs)
        
    def regenerate(self, context:UpdateContext):
        yield PatternGeneratorSharedStep( self.onTime, self.onValue )
        yield PatternGeneratorSharedStep( self.offTime, self.offValue )
        
#############################################################################

class CylonPatternStep(PatternGeneratorSharedStep):
    def __init__(self, index:int = 0, up:bool=True, *args, **kwds ):
        super().__init__(*args, **kwds)
        self._index = index
        self._up = up
        
    
    def startValue( self, index, context:UpdateContext ):
        return self._startValue if index == self._index else self._endValue
    
    def endValue( self, index, context:UpdateContext ):
        return self._startValue if index == self._index else self._endValue

    def intermediateValue( self, index, progression:ZeroToOne, context:UpdateContext ):
        if index == self._index: return self.startValue
        iOffset = self._index - index if self._up else index - self._index
        if iOffset > 0:
            return self._startValue + (self._endValue - self._startValue) * (progression/iOffset)
        else:
            return self._endValue
    
class Cylon( PatternGenerator ):
    def __init__(self,
                 *args,
                 sweepTime:TimeInSeconds = 1.0,
                 onValue:AnyLightValue = 1.0,
                 offValue:AnyLightValue = 0.0,
                 intermediateRefresh:TimeInSeconds = 0.1,
                 **kwargs
            ):
        self.sweepTime = sweepTime
        self.onValue = onValue
        self.offValue = offValue
        self.__movingUp = True
        self.intermediateRefresh:TimeInSeconds = intermediateRefresh
        super().__init__(*args,**kwargs)

        
    def regenerate(self, context:UpdateContext):
        sweepStepTime = self.sweepTime / self.target.lightCount
        if( self.__movingUp ):
            self.__movingUp = False
            for index in range( self.target.lightCount-1 ):
                yield CylonPatternStep( index, up=True,
                    duration=sweepStepTime, intermediateRefresh=self.intermediateRefresh, 
                    startValue = self.onValue, endValue = self.offValue  )
        else:
            self.__movingUp = True
            index = self.target.lightCount-1
            while index > 0:
                yield CylonPatternStep( index, up=False,
                    duration=sweepStepTime, intermediateRefresh=self.intermediateRefresh, 
                    startValue = self.onValue, endValue = self.offValue  )


                index -= 1

#############################################################################

