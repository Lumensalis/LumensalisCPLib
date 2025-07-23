from __future__ import annotations


#from LumensalisCP.common import *
#from LumensalisCP.Eval.common import *
from LumensalisCP.IOContext import *
from LumensalisCP.Lights.RGB import RGB, AnyRGBValue
from LumensalisCP.Lights.Light import Light, RGBLight
from LumensalisCP.Lights.Groups import LightGroup

from LumensalisCP.Eval.EvaluationContext import EvaluationContext
from LumensalisCP.Eval.Evaluatable import evaluate, Evaluatable
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.common import *
if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
#############################################################################

class Pattern(NamedLocalIdentifiable):

    class KWDS(TypedDict):
        name: NotRequired[str]
        whenOffset: NotRequired[TimeInSecondsConfigArg]
        startingSpeed: NotRequired[TimeInSecondsConfigArg]
    
    
    def __init__(self,  target:LightGroup, name:Optional[str]=None, 
                 whenOffset:TimeInSecondsConfigArg=0.0, startingSpeed:TimeInSecondsEvalArg=1.0 ):
        super().__init__(name=name)
        self.__running = False
        self.__speed:TimeInSecondsEval =toTimeInSecondsEval( startingSpeed)
        assert target is not None, f"target LightGroup must be provided when creating {self.__class__.__name__} Pattern"
        self.__target = target
        
        self.__whenOffset:TimeInSecondsEval =toTimeInSecondsEval( whenOffset )

    @property
    def whenOffset(self) -> TimeInSecondsEval : return self.__whenOffset
    
    @whenOffset.setter
    def whenOffset(self,offset:TimeInSecondsEval): self.__whenOffset = offset
    
    def offsetWhen( self, context:EvaluationContext ) -> TimeInSeconds:
        return  context.when + self.__whenOffset # type: ignore

    _theManager:MainManager


    @property
    def target(self) -> LightGroup : return  self.__target
    
    @property
    def speed(self) -> TimeInSecondsEval: return self.__speed
    
    @speed.setter
    def speed(self, value:TimeInSecondsEval): self.setSpeed(value)
    
    @property
    def running(self) -> bool: return self.__running

    @running.setter
    def running(self, running:bool): self.setRunning(running)

    def setSpeed(self, value:TimeInSecondsEval, context:Optional[EvaluationContext]=None ): # pylint: disable=unused-argument
        self.__speed = value

    def setRunning(self, value:bool, context:Optional[EvaluationContext]=None ): # pylint: disable=unused-argument
        self.__running = value

    def refresh( self, context:EvaluationContext ) -> None:
        raise NotImplementedError

    def main(self):
        if Pattern._theManager is None:
            Pattern._theManager = LumensalisCP.Main.Manager.MainManager.theManager
            assert Pattern._theManager is not None
            
        return Pattern._theManager
    
#############################################################################

class OnOffPattern( Pattern ): # pylint: disable=abstract-method
    
    class KWDS(Pattern.KWDS):
        onValue: NotRequired[RGBEvalArg]
        offValue: NotRequired[RGBEvalArg]
        
    def __init__(self,
                target:LightGroup, name:Optional[str]=None, 
                onValue:RGBEvalArg =  RGB.WHITE,
                offValue:RGBEvalArg = RGB.BLACK,
                **kwargs
            ):
        """ base for patterns which vary between on and off colors

        :param target: group to be controlled
        :type target: LightGroup
        :param name: name of the pattern, defaults to None
        :type name: Optional[str], optional
        :param onValue: value or Evaluatable convertible to RGB
        :type onValue: RGBEvalArg, optional
        """
        self._onValue = onValue
        self._offValue = offValue

        super().__init__( target=target,name=name, **kwargs)

#############################################################################
        
class PatternGeneratorStep(object):
    def __init__( self, 
                 startValue: AnyRGBValue, 
                 endValue: Optional[AnyRGBValue] =  None, 
                 duration: TimeInSeconds=TimeInSeconds(1.0),
                 intermediateRefresh: TimeInSeconds|None = None,
            ):
        self._startValue = startValue
        self._endValue:AnyRGBValue = endValue or startValue
        self.duration = duration
        self.intermediateRefresh = intermediateRefresh
    
    def startValue( self, index:int, context:EvaluationContext ): # pylint: disable=unused-argument
        return context.valueOf( self._startValue )
    
    def endValue( self, index:int , context:EvaluationContext ): # pylint: disable=unused-argument
        return context.valueOf( self._endValue )

    def intermediateValue( self, index, progression:ZeroToOne, context:EvaluationContext ):
        start = self.startValue(index,context=context)
        return start + ( (self.endValue(index,context=context) - start ) * progression )

#############################################################################

class MultiLightPatternStep(PatternGeneratorStep):
    def __init__(self, duration, starts:Sequence[AnyRGBValue], ends:Sequence[AnyRGBValue], **kwds ):
        super().__init__(duration=duration, **kwds)
        self.__starts = starts
        self.__ends = ends
    
    @override
    def startValue( self, index:int, context:EvaluationContext ):
        return context.valueOf( self.__starts[index] )
    
    @override
    def endValue( self, index:int, context:EvaluationContext ):
        return context.valueOf( self.__ends[index] )

#############################################################################

class PatternGenerator(Pattern):
    class KWDS(Pattern.KWDS):
        intermediateRefresh: NotRequired[TimeInSecondsConfigArg]
        
    def __init__(self, *args, intermediateRefresh:Optional[TimeInSeconds]=None,  **kwargs ): # pylint: disable=unused-argument
        super().__init__( *args, **kwargs )
        self.__nextStep = 0.0
        self.__nextRefresh = 0.0
        self.__step:PatternGeneratorStep|None = None
        self.__gen: Iterator[PatternGeneratorStep]|None = None
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
        
    def refresh( self, context:EvaluationContext ):
        if self.__nextRefresh < context.when:
            context.activeFrame.snap(f"PGRefresh-{self.name}")
            if self.__nextStep < context.when:
                self.stepForward( context )
            else:
                assert self.__step is not None
                assert self.__step.intermediateRefresh is not None
                when = self.offsetWhen( context )
                duration = context.valueOf(self.__step.duration)
                progression = (self.__nextStep - when) / duration
                self.__nextRefresh = min(  self.__nextStep,
                            when + self.__step.intermediateRefresh )
                self.__intermediateCount += 1
                for lx, light in enumerate(self.target.lights): # pylint: disable=unused-variable
                    self.target[lx] = self.__step.intermediateValue(lx,progression,context)
                    #light.setValue( self.__step.intermediateValue(lx,progression,context), context=context )
    
    def stepForward( self, context:EvaluationContext ):
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

        for lx, light in enumerate(self.target.lights):  # pylint: disable=unused-variable
            self.target[lx].set( self.__step.startValue(lx,context) , context )
            #light.setValue( self.__step.startValue(lx,context), context=context )

    def regenerate(self, context:EvaluationContext) -> Iterator[PatternGeneratorStep]:
        raise NotImplementedError

    #def setRunning(self, value:bool, context:Optional[EvaluationContext]=None ):
    #    super().setRunning(value, context)

#############################################################################
