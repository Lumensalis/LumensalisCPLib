from __future__ import annotations


from LumensalisCP.ImportProfiler import  getImportProfiler
__profileImport = getImportProfiler( __name__, globals() )

#from LumensalisCP.common import *
#from LumensalisCP.Eval.common import *
from LumensalisCP.IOContext import *
from LumensalisCP.Lights.RGB import *


#from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.common import *
from LumensalisCP.util.bags import Bag

if TYPE_CHECKING:
    from LumensalisCP.Lights.Groups import LightGroup
    from LumensalisCP.Eval.EvaluationContext import EvaluationContext

    #from LumensalisCP.Main.Manager import MainManager
#############################################################################

from LumensalisCP.Lights.Pattern import Pattern

#############################################################################
        
class PatternGeneratorStep(CountedInstance):
    class KWDS(TypedDict):
        startValue: Required[AnyRGBValue]
        endValue: NotRequired[AnyRGBValue]
        duration: NotRequired[TimeSpanInSeconds]
        intermediateRefresh: NotRequired[TimeSpanInSeconds]

    def __init__( self, 
                 startValue: Optional[AnyRGBValue] = 0, 
                 endValue: Optional[AnyRGBValue] =  None, 
                 duration: TimeSpanInSeconds=1.0,
                 intermediateRefresh: TimeSpanInSeconds|None = None,
            ):
        super().__init__()
        self._startValue = startValue
        self._endValue = endValue if endValue is not None else startValue
        self.duration = duration
        self.intermediateRefresh = intermediateRefresh
    
    def startValue( self, index:int, context:EvaluationContext ): # pylint: disable=unused-argument
        return context.valueOf( self._startValue )
    
    def endValue( self, index:int , context:EvaluationContext ): # pylint: disable=unused-argument
        return context.valueOf( self._endValue )

    def intermediateValue( self, index:int, progression:ZeroToOne, context:EvaluationContext ):
        start = self.startValue(index,context=context)
        return start + ( (self.endValue(index,context=context) - start ) * progression )

#############################################################################

class MultiLightPatternStep(PatternGeneratorStep):
    class KWDS(PatternGeneratorStep.KWDS):
        
        starts: Required[list[AnyRGBValue]]
        ends: Required[list[AnyRGBValue]]

    def __init__(self, starts:list[AnyRGBValue], ends:list[AnyRGBValue],  startValue:Optional[AnyRGBValue] = None,
                 **kwds:Any # Unpack[PatternGeneratorStep.KWDS]
                   ) -> None: # type: ignore
        kwds.setdefault('startValue', starts[0])
        assert len(starts) == len(ends), "starts and ends must be same length"
        assert len(starts) > 0, "starts and ends must not be empty"
        super().__init__( **kwds)
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
    RFD_refreshRate:ClassVar[TimeSpanInSeconds] = 0.041 # 24 FPS
    class KWDS(Pattern.KWDS):
        intermediateRefresh: NotRequired[TimeSpanInSeconds]
        
    def __init__(self, target:LightGroup, 
                 intermediateRefresh:Optional[TimeSpanInSeconds]=None,  
                 **kwargs:Unpack[Pattern.KWDS] ): # pylint: disable=unused-argument
        super().__init__( target, **kwargs )
        self.__nextStep = 0.0
        self.__nextPatternRefresh = 0.0
        self.__step:PatternGeneratorStep|None = None
        self.__gen: Iterator[PatternGeneratorStep]|None = None
        self.__stepCount = 0
        self.__intermediateCount = 0
        self.intermediateRefresh = intermediateRefresh
    
    def stats(self)->Bag:
        return Bag(
                    nextStep = self.__nextStep, 
                    nextRefresh = self.__nextPatternRefresh, 
                     # = self.__step, 
                    stepCount = self.__stepCount, 
                    intermediateCount = self.__intermediateCount,
        )

    def patternRefresh( self, context:EvaluationContext ):
        if self.__nextPatternRefresh < context.when:
            context.snap("PGRefresh", self.name)
            if self.__nextStep < context.when:
                self.stepForward( context )
            else:
                assert self.__step is not None
                assert self.__step.intermediateRefresh is not None
                when = self.offsetWhen( context )
                duration = context.valueOf(self.__step.duration)
                progression = (self.__nextStep - when) / duration
                self.__nextPatternRefresh = min(  self.__nextStep,
                            when + self.__step.intermediateRefresh )
                self.__intermediateCount += 1
                for lx, _ in enumerate(self.target.lights): # pylint: disable=unused-variable
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
            self.__nextPatternRefresh = context.when + self.__step.intermediateRefresh
        else:
            self.__nextPatternRefresh = self.__nextStep

        for lx, _ in enumerate(self.target.lights):  # pylint: disable=unused-variable
            self.target[lx].set( self.__step.startValue(lx,context) , context )
            #light.setValue( self.__step.startValue(lx,context), context=context )

    def regenerate(self, context:EvaluationContext) -> Iterator[PatternGeneratorStep]:
        raise NotImplementedError

    #def setRunning(self, value:bool, context:Optional[EvaluationContext]=None ):
    #    super().setRunning(value, context)

#############################################################################
__profileImport.complete()
