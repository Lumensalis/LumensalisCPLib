from __future__ import annotations


from LumensalisCP.ImportProfiler import  getImportProfiler
__profileImport = getImportProfiler( __name__, globals() )

from LumensalisCP.IOContext import *
from LumensalisCP.Lights.RGB import *
from LumensalisCP.Lights.Groups import LightGroup

from LumensalisCP.Eval.EvaluationContext import EvaluationContext
from LumensalisCP.Temporal.Refreshable import RefreshableNAP

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager

#############################################################################
__profileImport.parsing()

class Pattern(RefreshableNAP):
    RENDER_REFRESHABLE_LIST = True

    RFD_refreshRate:ClassVar[TimeSpanInSeconds] = 0.041 
    class KWDS(RefreshableNAP.KWDS):
        whenOffset: NotRequired[TimeInSecondsConfigArg]
        startingSpeed: NotRequired[TimeInSecondsConfigArg]
    
    
    def __init__(self,  target:LightGroup, 
                 whenOffset:TimeInSecondsConfigArg=0.0,
                   startingSpeed:TimeInSecondsEvalArg=1.0, 
                   **kwargs:Unpack[RefreshableNAP.KWDS] 
                ) -> None:
        
        if not Pattern.RENDER_REFRESHABLE_LIST:
            del kwargs['autoList']

        super().__init__(**kwargs)
        #self.__running = False
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

    @property
    def target(self) -> LightGroup : return  self.__target
    
    @property
    def speed(self) -> TimeInSecondsEval: return self.__speed
    
    @speed.setter
    def speed(self, value:TimeInSecondsEval): self.setSpeed(value)

    if False:
        @property
        def running(self) -> bool: return self.__running

        @running.setter
        def running(self, running:bool): self.setRunning(running)

    def setSpeed(self, value:TimeInSecondsEval, context:Optional[EvaluationContext]=None ): # pylint: disable=unused-argument
        self.__speed = value

    def setRunning(self, value:bool, context:Optional[EvaluationContext]=None ): # pylint: disable=unused-argument
        self.__running = value

    def patternRefresh( self, context:EvaluationContext ) -> None:
        raise NotImplementedError

    def derivedRefresh(self, context: EvaluationContext) -> None:
        #if self.enableDbgOut:
        self.patternRefresh(context)
    
    def main(self) -> MainManager:
        return getMainManager()
    
#############################################################################

class OnOffPattern( Pattern ): # pylint: disable=abstract-method
    
    class KWDS(Pattern.KWDS):
        onValue: NotRequired[RGBEvalArg]
        offValue: NotRequired[RGBEvalArg]
        
    def __init__(self,
                target:LightGroup, 
                onValue:RGBEvalArg =  Colors.WHITE,
                offValue:RGBEvalArg = Colors.BLACK,
                **kwargs:Unpack[Pattern.KWDS]
            ):
        """ base for patterns which vary between on and off colors

        :param target: group to be controlled
        :type target: LightGroup
        :param name: name of the pattern, defaults to None
        :type name: Optional[str], optional
        :param onValue: value or Evaluatable convertible to RGB
        :type onValue: RGBEvalArg, optional
        """
        self._onValue = toRGBEval(onValue)
        self._offValue = toRGBEval(offValue)

        super().__init__( target=target, **kwargs)

    def getOnValue(self, context:EvaluationContext) -> RGB:
        """ get the on value for this pattern

        :param context: the context to evaluate in
        :type context: EvaluationContext
        :return: the on value as an RGB
        :rtype: RGB
        """
        return RGB.toRGB( context.valueOf(self._onValue) )

    def getOffValue(self, context:EvaluationContext) -> RGB:
        """ get the off value for this pattern

        :param context: the context to evaluate in
        :type context: EvaluationContext
        :return: the off value as an RGB
        :rtype: RGB
        """
        return RGB.toRGB( context.valueOf(self._offValue) )
    
#############################################################################
        
#############################################################################
__profileImport.complete()