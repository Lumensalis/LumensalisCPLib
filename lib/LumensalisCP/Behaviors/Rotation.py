from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayMotionImport = getImportProfiler( globals() ) # "Motion"

from LumensalisCP.Behaviors._common import *
from LumensalisCP.Behaviors.Actor import Actor
from LumensalisCP.Behaviors.Behavior import Behavior
from LumensalisCP.Behaviors.Motion import Motion

# pyright: reportPrivateUsage=false

#############################################################################
class Spinner(Actor,Tunable):
    """ A continuously rotating drive, like a stepper or DC motor """

    def __init__(self, **kwds:Unpack[Actor.KWDS]):
        Actor.__init__( self, **kwds )
        Tunable.__init__(self)
        #self.defaultJogSpeed:ZeroToOneEval = 0.5
        #self.manualSpeed = TunableSettingT[PlusMinusOne](startingValue=0,onChange=self._onManualSpeedChange)
        self.manualOverride = TunableBoolSettingT[Self](self, startingValue=False, onChange=Spinner._onManualOverrideChange)
        self._inManualControl = False

    @tunableZeroToOne(0.5)
    def defaultJogSpeed(self, setting:TunableZeroToOneSetting[Spinner], context:EvaluationContext ) -> None:
        if self.enableDbgOut: self.dbgOut("defaultJogSpeed changed to %s", setting.value)
        return

    @tunablePlusMinusOne(0.0)
    def defaultDirectionalSpeed(self, setting:TunablePlusMinusOneSetting[Spinner], context:EvaluationContext ) -> None:
        if self.enableDbgOut: self.dbgOut("defaultDirectionalSpeed changed to %s", setting.value)
        return 

    @tunablePlusMinusOne(0.0)
    def manualSpeed(self, setting:TunablePlusMinusOneSetting[Spinner], context:EvaluationContext ) -> None:
        if self._inManualControl:
            if self.enableDbgOut: self.dbgOut("manualSpeed changed to %s", setting.value)
            self._setManualSpeed( setting.value, context=context )
        else:
            if self.enableDbgOut: self.dbgOut("manualSpeed changed to %s, (ignored)", setting.value)

    def _onManualOverrideChange(self, setting:TunableSetting[bool,bool,Self], context:EvaluationContext ) -> None:
        if self.enableDbgOut: self.dbgOut("manualOverride changed to %s", setting.value)
        self._inManualControl = setting.value
        if not setting.value:
            self._clearManualSpeed(context=context)

    def spin(self, directionalSpeed:Optional[PlusMinusOneEvalArg] = 0, duration:Optional[TimeInSecondsEvalArg]=None, context:Optional[EvaluationContext]=None) -> Behavior:
        raise NotImplementedError("open method must be implemented in subclass")

    def stop(self, context:Optional[EvaluationContext]=None) -> Behavior:
        raise NotImplementedError("stop method must be implemented in subclass")
    
    def _setManualSpeed( self, directionalSpeed:PlusMinusOne, context:EvaluationContext) -> None:
        raise NotImplementedError("setManualSpeed method must be implemented in subclass")

    def _clearManualSpeed( self, context:EvaluationContext) -> None:
        raise NotImplementedError("clearManualSpeed method must be implemented in subclass")

    def _move( self, movement:SpinMovement|None,
                directionalSpeed:PlusMinusOneEvalArg,
                duration:Optional[TimeInSecondsEvalArg]=None,
                context:Optional[EvaluationContext]=None) -> None:
            raise NotImplementedError("move method must be implemented in subclass")


#############################################################################
class SpinMovement(Motion):
    """ rotation behavior for a Spinner"""

    class KWDS(Motion.KWDS):
        directionalSpeed:NotRequired[PlusMinusOneEvalArg]
        nextBehavior:NotRequired[SpinMovement]

    def __init__(self, actor:Spinner, 
                 directionalSpeed:PlusMinusOneEvalArg = 0,
                 nextBehavior:Optional[SpinMovement]=None,
                  **kwds:Unpack[Motion.KWDS]) -> None:
        super().__init__(actor, **kwds)
        self.directionalSpeed = directionalSpeed
        self.nextBehavior = nextBehavior

    def set( self, 
                directionalSpeed:Optional[PlusMinusOneEvalArg]= None,
                context:Optional[EvaluationContext]=None
                ):
        if context is None:
            context=UpdateContext.fetchCurrentContext(context)

        if ( directionalSpeed is None or self.directionalSpeed == directionalSpeed):
            # nothing changed
            if self.enableDbgOut: self.dbgOut("set: %s|%s", 
                    context.valueOf(directionalSpeed), directionalSpeed)
            return
        self.directionalSpeed = directionalSpeed
        
        if self.actor.currentBehavior is self:
            self.spinner._move( self, self.directionalSpeed, context=UpdateContext.fetchCurrentContext(context) ) 
    
    def derivedEnter(self, context:EvaluationContext) -> None:
        if self.enableDbgOut: self.dbgOut("derivedEnter( %r )", self )
        self.derivedBeginMove(context)
    
    def derivedBeginMove( self,context:EvaluationContext )-> None:
        if self.enableDbgOut: self.dbgOut("derivedBeginMove( %r )", self )
        self.spinner._move( self, self.directionalSpeed, context=context )

    def derivedEndMove( self,context:EvaluationContext )-> None:
        if self.enableDbgOut: self.dbgOut("derivedEndMove( %r )", self )
        self.spinner._move( self, 0, context=context )
    
    
    def derivedExit(self, context:EvaluationContext) -> None:
        if self.enableDbgOut: self.dbgOut("derivedExit( %r )", self )
        if self.nextBehavior is None:
            self.spinner._move( self, 0, context=context )

    spinner:ClassVar[Spinner] = Behavior.actor  # type: ignore

    def __repr__(self) -> str:
        return f"({self.__class__.__name__}@ {hex(id(self))} {self.name!r} directionalSpeed={self.directionalSpeed})"
    
class SpinTimedMovement(SpinMovement):
    """ timed movement behavior
    """
    # pylint: disable=protected-access

    duration:TimeInSecondsEval
        
    def __init__(self, actor:Spinner,
            duration:TimeInSecondsEvalArg = 0, **kwds:Unpack[SpinMovement.KWDS] ):
        super().__init__(actor, **kwds)
        self.duration = toTimeInSecondsEval(duration)
        
    def setTimed( self, 
                directionalSpeed:Optional[PlusMinusOneEvalArg]= None,
                duration:Optional[TimeInSecondsEvalArg]=None, 
                context:Optional[EvaluationContext]=None
                ):
        """Reset the servo movement parameters."""
        context =UpdateContext.fetchCurrentContext(context)

        def isChange( arg:Any, attr:Any) -> bool:
            if arg is None: return False
            if isinstance(arg, Evaluatable):
                return arg is not attr
            elif isinstance(attr,Evaluatable):
                return True
            assert isinstance(arg, (float,int))
            return context.valueOf(arg) != attr
    
        if not (isChange(directionalSpeed,self.directionalSpeed) 
                        or isChange(duration, self.duration) ):
            # nothing changed
            if self.actor.currentBehavior is not self:
                if self.enableDbgOut: self.dbgOut("setTimed: no change from %s, %s (%s, %s)  returning", 
                            directionalSpeed, duration, self.directionalSpeed, self.duration)
                return
        else:
            if duration is not None:
                self.duration = toTimeInSecondsEval(duration)
            if directionalSpeed is not None:
                self.directionalSpeed = directionalSpeed

        if self.enableDbgOut: self.dbgOut("setTimed: %s|%s, %s|%s", 
                                            context.valueOf(self.directionalSpeed), self.directionalSpeed,
                                            context.valueOf(self.duration), self.duration)
        if self.actor.currentBehavior is self:
            self.spinner._move( self, self.directionalSpeed, self.duration, ) # type: ignore
    
    def derivedBeginMove( self,context:EvaluationContext )-> None:
        vds = context.valueOf(self.directionalSpeed)
        vdt = context.valueOf(self.duration)
        if self.enableDbgOut: self.dbgOut("derivedBeginMove(%s,%s)", vds, vdt)
        self.spinner._move( self, vds, vdt, context )
        self.spinner.activate(context=context)
    
    def derivedEndMove( self,context:EvaluationContext )-> None:
        if self.enableDbgOut: self.dbgOut("derivedEndMove")
        self.spinner.deactivate(context=context)
        self.spinner._move( self, 0, None, context )
    
    def __repr__(self) -> str:
        return f"({self.__class__.__name__}@ {hex(id(self))} {self.name!r} directionalSpeed={self.directionalSpeed}, duration={self.duration})"
    # def derivedExit(self, context:EvaluationContext) -> None: ...

class DCMotorSpinner(Spinner):
    """ Spinner driven by servo

    Args:
        Spinner (_type_): _description_
    """

    class KWDS(Spinner.KWDS):
        lowerLimit:NotRequired[InputSource]
        upperLimit:NotRequired[InputSource]
        defaultDirectionalSpeed:NotRequired[PlusMinusOneEvalArg]

    @tunableZeroToOne(1.0)
    def maxSpeed(self, setting:TunableZeroToOneSetting[Self], context:EvaluationContext) -> None:
        if self.enableDbgOut: self.dbgOut("maxSpeed changed to %s", setting.value)
        return

    @tunableZeroToOne(1.0)
    def minSpeed(self, setting:TunableZeroToOneSetting[Self], context:EvaluationContext) -> None:
        if self.enableDbgOut: self.dbgOut("minSpeed changed to %s", setting.value)
        return
    
    @tunablePlusMinusOne(0.0)
    def defaultDirectionalSpeed(self, setting:TunablePlusMinusOneSetting[Self], context:EvaluationContext) -> None:
        if self.enableDbgOut: self.dbgOut("defaultDirectionalSpeed changed to %s", setting.value)
        return 

    def __init__(self,
            inA:OutputTarget,
            inB:OutputTarget,
            defaultDirectionalSpeed:Optional[PlusMinusOneEvalArg] = None,
            lowerLimit:Optional[InputSource] = None,
            upperLimit:Optional[InputSource] = None,
            **kwds:Unpack[Spinner.KWDS]
        ):
        super().__init__(**kwds)
        self.inA = inA
        self.inB = inB
        self.defaultDirectionalSpeed = toPlusMinusOneEval(defaultDirectionalSpeed, 0.0)

        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit
        self.idle = SpinMovement(self, name="Idle", directionalSpeed=0 )   
        self.stopped = SpinMovement(self, name="Stopped", directionalSpeed=0 )   
        self.joggingLeft = SpinTimedMovement(self, name="JogLeft", directionalSpeed=-0.5,duration=0.5 )
        self.joggingRight = SpinTimedMovement(self, name="JogRight", directionalSpeed=0.5,duration=0.5 )
        self.spinning = SpinMovement(self, name="Spin", directionalSpeed=0 )   
        self.spinningManual = SpinMovement(self, name="ManualSpin", directionalSpeed=0 )   
        self.spinningTimed = SpinTimedMovement(self, name="TimedSpin", directionalSpeed=0 )


        self.__moveStartTime:TimeInSeconds=getOffsetNow()
        self.__moveEndTime:TimeInSeconds|None = None
        self.__targetSpeed:PlusMinusOne = 0
        
        if self.enableDbgOut:
            self.setEnableDebugWithChildren(self.enableDbgOut)

    def __repr__(self) -> str:
        return f"({self.__class__.__name__}@ {hex(id(self))} {self.name!r} inA={self.inA}, inB={self.inB}, defaultDirectionalSpeed={self.defaultDirectionalSpeed})"
    
    def spin(self, directionalSpeed:Optional[PlusMinusOneEvalArg] = 0, 
                duration:Optional[TimeInSecondsEvalArg]=None, 
                context:Optional[EvaluationContext]=None) -> SpinMovement:
        if context is None:
            context = UpdateContext.fetchCurrentContext(context)

        if self.enableDbgOut:
            self.infoOut(f"spin: {directionalSpeed}|{context.valueOf(directionalSpeed)}, duration: {duration}|{context.valueOf(duration)}")

        if duration is not None:
            self.spinningTimed.setTimed(directionalSpeed=directionalSpeed, duration=duration, context=context)
            self.setCurrentBehavior(self.spinningTimed, reset=True, context=context)
            return self.spinningTimed

        else:
            self.spinning.set(directionalSpeed=directionalSpeed, context=context )
            self.setCurrentBehavior(self.spinning, reset=True, context=context)
            return self.spinning

    def stop(self, context:Optional[EvaluationContext]=None) -> Motion:
        self.setCurrentBehavior(self.stopped, reset=True, context=context)
        return self.stopped


            

    def _complete(self, movement:SpinMovement, context:EvaluationContext):
        self.infoOut( f"_complete {movement}" )
        if movement.nextBehavior is not None:
            self.setCurrentBehavior(movement.nextBehavior)
        else:
            self.setCurrentBehavior(self.stopped)

    def derivedRefresh(self,context:EvaluationContext) -> None:
        if self.__moveEndTime is not None:
            if self.enableDbgOut: self.dbgOut("derivedRefresh: moveEndTime=%s, now=%s", self.__moveEndTime, context.when)
            if self.__moveEndTime <= context.when:
                self.__moveEndTime = None
                if self.currentBehavior is not None:
                    self._complete(self.currentBehavior, context)

    def _move( self, movement:SpinMovement|None,
                directionalSpeed:PlusMinusOneEvalArg,
                duration:Optional[TimeInSecondsEvalArg]=None,
                context:Optional[EvaluationContext]=None) -> None:
        
        if context is None:
            context = UpdateContext.fetchCurrentContext(context)

        self.__moveStartTime = getOffsetNow()
        if duration is not None:
            duration = context.valueOf(duration)
            self.__moveEndTime = self.__moveStartTime + duration
        else:
            self.__moveEndTime = None

        vds = context.valueOf(directionalSpeed)
        if self.enableDbgOut:
            self.infoOut(f"_move: {vds}, duration: {duration}")
        self._setSpeed(vds, context)

    def _setSpeed( self, directionalSpeed:PlusMinusOne, context:EvaluationContext) -> None:
        self.__targetSpeed = directionalSpeed
        if abs(directionalSpeed) < self.minSpeed.value:
            directionalSpeed = 0
        if directionalSpeed < 0:
            inA, inB = (-min(self.maxSpeed.value, directionalSpeed), 0)
        elif directionalSpeed > 0:
            inA, inB = (0, min(self.maxSpeed.value, directionalSpeed))
        else:
            inA, inB = (0, 0)

        if self.enableDbgOut:
            self.infoOut(f"_setSpeed: {directionalSpeed}, inA: {inA}, inB: {inB}")
        self.inA.set(inA, context)
        self.inB.set(inB, context)

    def _setManualSpeed( self, directionalSpeed:PlusMinusOne, context:EvaluationContext) -> None:
        self.spinningManual.set(directionalSpeed=directionalSpeed, context=context)
        self.setCurrentBehavior( self.spinningManual, context=context )

    def _clearManualSpeed( self, context:EvaluationContext) -> None:
        self.setCurrentBehavior( self.stopped, context=context )
        

    # def setEnableDebugWithChildren(self, setting:bool):            
    def _derivedSetEnableDebugWithChildren( self, setting:bool, *args:Any, **kwds:StrAnyDict) -> None:
        self.enableDbgOut = setting
        self.idle.enableDbgOut = setting
        self.stopped.enableDbgOut = setting
        self.joggingLeft.enableDbgOut = setting
        self.joggingRight.enableDbgOut = setting
        self.spinning.enableDbgOut = setting
        self.spinningManual.enableDbgOut = setting
        self.spinningTimed.enableDbgOut = setting
        self.manualSpeed.enableDbgOut = setting

_sayMotionImport.complete(globals())