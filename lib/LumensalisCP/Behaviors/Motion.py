from __future__ import annotations

from LumensalisCP.Main.PreMainConfig import ImportProfiler
_sayMotionImport = ImportProfiler( "Motion" )

from LumensalisCP.Behaviors._common import *
from LumensalisCP.Behaviors.Behavior import Behavior, Actor
from LumensalisCP.Gadgets.Servos import LocalServo

class Motion(Behavior):
    """
    Base class for motion behaviors.
    """

    def __init__(self, actor:Actor, name:str|None = None):
        super().__init__(actor, name)

class Door(Actor):
    
    def __init__(self, **kwds:Unpack[Actor.KWDS]):
        
        super().__init__( **kwds )
        
    def open(self, speed:TimeInSeconds|None = None, context:Optional[EvaluationContext]=None) -> Behavior:
        raise NotImplementedError("open method must be implemented in subclass")

    def close(self, speed:TimeInSeconds|None = None, context:Optional[EvaluationContext]=None) -> Behavior:
        raise NotImplementedError("open method must be implemented in subclass")
    
    def setSpeed(self, speed:TimeInSeconds, context:Optional[EvaluationContext]=None) -> None:
        raise NotImplementedError("setSpeed method must be implemented in subclass")

    def stop(self, context:Optional[EvaluationContext]=None) -> Behavior:
        raise NotImplementedError("stop method must be implemented in subclass")

class ServoMovement(Motion):
    """_summary_

    Args:
        Motion (_type_): _description_
    """
    # pylint: disable=protected-access
    
    # type: actor:"ServoDoor"
    target:Degrees = 0.0
    speed:DegreesPerSecond = 10
    nextBehavior:"ServoMovement|None"
        
    def __init__(self, actor:"ServoDoor", name:str|None = None,
            target:Degrees|None = None, speed:DegreesPerSecond|None = None ):
        super().__init__(actor, name)
        self.reset( target=target, speed=speed)
        self.nextBehavior = None
        
    def reset( self, target:Optional[Degrees]=None, speed:DegreesPerSecond|None = None ):
        """Reset the servo movement parameters."""
        if ( target is None or self.target == target) and (speed is None or speed == self.speed ): return
        if target is not None: self.target = target
        if speed is not None: self.speed = speed
        if self.actor.currentBehavior is self:
            self.actor._servo.moveTo( self.target, self.speed, UpdateContext.fetchCurrentContext(None) ) # type: ignore
        #    self.actor.setCurrentBehavior(self, reset=True)

    def activate( self, target:Optional[Degrees]=None, 
                 speed:DegreesPerSecond|None = None,
                 context:Optional[EvaluationContext]=None # pylint: disable=unused-argument
                ) -> "ServoMovement":
        self.reset( target=target,speed=speed)
        if self.actor.currentBehavior is not self:
            self.actor.setCurrentBehavior(self)
        return self

    def _complete(self,**kwds:StrAnyDict):
        self.infoOut( f"_complete {kwds}" )
        if self.nextBehavior is not None:
            self.nextBehavior.activate()
        
    def enter(self, context:EvaluationContext):
        super().enter(context)
        if self.enableDbgOut: self.dbgOut( f"enter moveTo {self.target} at {self.speed}" )
        self.actor._servo.moveTo( self.target, self.speed, context )  # type: ignore
        self.actor._servo.onMoveComplete( self._complete )  # type: ignore
    
    def exit(self, context:EvaluationContext):
        self.actor._servo.onMoveComplete( None )  # type: ignore
        super().exit(context)
        

class ServoDoor(Door):
    """ Door driven by servo

    Args:
        Door (_type_): _description_
    """
    servo:LocalServo
    closedPosition:Degrees 
    openPosition:Degrees 
    defaultSpeed:TimeInSecondsEval 
    openedSensor:InputSource|None
    closedSensor:InputSource|None

    class KWDS(Door.KWDS):
        closedPosition:NotRequired[Degrees]
        openPosition:NotRequired[Degrees]
        defaultSpeed:NotRequired[TimeInSecondsEvalArg]
        openedSensor:NotRequired[InputSource]
        closedSensor:NotRequired[InputSource]
    
    def __init__(self,
            servo:LocalServo,
            closedPosition:Degrees|None = None,
            openPosition:Degrees|None = None,
            defaultSpeed:TimeInSecondsEvalArg|None = None,
            openedSensor:InputSource|None = None,
            closedSensor:InputSource|None = None,
            **kwds:Unpack[Door.KWDS]
        ):
        super().__init__(**kwds)
        self.servo = servo
        
        self.closedPosition = closedPosition if closedPosition is not None else 45.0
        self.openPosition = openPosition if openPosition is not None else 75.0
        self.defaultSpeed = toTimeInSecondsEval( defaultSpeed, 5.0 )
        self.openedSensor = openedSensor
        self.closedSensor = closedSensor
        self.opening = ServoMovement(self, "Opening", target=self.openPosition  )   
        self.closing = ServoMovement(self, "Closing", target=self.closedPosition )
        self.opened = ServoMovement(self, "Opened", target=self.openPosition )
        self.closed = ServoMovement(self, "Closed", target=self.closedPosition )
        self.moving = ServoMovement(self, "Moving")
        self.stopped = ServoMovement(self, "Stopped")
        self.opening.nextBehavior = self.opened
        self.closing.nextBehavior = self.closed
        if self.enableDbgOut:
            self.setEnableDebugWithChildren(self.enableDbgOut)
    
    @property
    def span(self) -> Degrees:
        return  self.openPosition - self.closedPosition 
    
    def convertSpeed(self, speed:TimeInSeconds) -> DegreesPerSecond:
        return speed/self.span
    
    def setSpeed(self, speed:TimeInSeconds, context:Optional[EvaluationContext]=None) -> None:
        raise NotImplementedError("setSpeed method must be implemented in subclass")
    
    @property
    def openRatio(self):
        return (self.servo.lastSetAngle - self.closedPosition) - self.span
    
    # def setEnableDebugWithChildren(self, setting:bool):            
    def _derivedSetEnableDebugWithChildren( self, setting:bool, *args:Any, **kwds:StrAnyDict) -> None:
        self.enableDbgOut = setting
        self.opening.enableDbgOut = setting
        self.closing.enableDbgOut = setting
        self.opened.enableDbgOut = setting
        self.closed.enableDbgOut = setting
        self.moving.enableDbgOut = setting
        self.stopped.enableDbgOut = setting
        self.servo.enableDbgOut = setting
        
    def open(self, speed:TimeInSeconds|None = None, context:Optional[EvaluationContext]=None) -> Behavior:
        return self.opening.activate(speed=speed, target=self.openPosition, context=context)
        
    def close(self, speed:TimeInSeconds|None = None, context:Optional[EvaluationContext]=None) -> Behavior:
        return self.closing.activate(speed=speed, target=self.closedPosition, context=context)

    def stop(self, context:Optional[EvaluationContext]=None) -> Motion:
        return self.stopped.activate(target=self.servo.lastSetAngle, context=context)

    def moveTo(self, target:Degrees, speed:TimeInSeconds|None = None, context:Optional[EvaluationContext]=None) -> None:
        self.moving.activate(speed=speed, target=target, context=context)

    def jog(self, offset:Degrees, speed:TimeInSeconds|None = None, context:Optional[EvaluationContext]=None) -> Motion:
        return self.moving.activate(speed=speed, target=self.servo.lastSetAngle + offset, context=context)
            
    #def addOpenTrigger( self, Input): pass
    
    def _moveCompleted(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        if self.enableDbgOut: self.dbgOut("ServoDoor move completed")

_sayMotionImport.complete()