
# from ..Scene import Scene, SceneTask

from LumensalisCP.IOContext import *
from LumensalisCP.Main.Profiler import Profiler
from .Behavior import Behavior, Actor
from ..Gadgets.Servos import LocalServo

import LumensalisCP.Main.Manager

class Motion(Behavior):
    """
    Base class for motion behaviors.
    """
    
    def __init__(self, actor:Actor, name:str|None = None):
        super().__init__(actor, name)
        


class Door(Actor):
    
    def __init__(self, name:str|None = None, main:"LumensalisCP.Main.Manager.MainManager"|None = None):
        super().__init__(name, main)
        
    def open(self, speed:TimeInSeconds|None = None, context:EvaluationContext|None=None) -> Behavior:
        raise NotImplementedError("open method must be implemented in subclass")

    def close(self, speed:TimeInSeconds|None = None, context:EvaluationContext|None=None) -> Behavior:
        raise NotImplementedError("open method must be implemented in subclass")
    
    def setSpeed(self, speed:TimeInSeconds, context:EvaluationContext|None=None) -> Behavior:
        raise NotImplementedError("setSpeed method must be implemented in subclass")

    def stop(self, context:EvaluationContext|None=None) -> Behavior:
        raise NotImplementedError("stop method must be implemented in subclass")

class ServoMovement(Motion):
    """_summary_

    Args:
        Motion (_type_): _description_
    """
    actor:"ServoDoor"
    target:Degrees = 0.0
    speed:DegreesPerSecond = 10
    
    def __init__(self, actor:"ServoDoor", name:str|None = None,
            target:Degrees|None = None, speed:DegreesPerSecond|None = None ):
        super().__init__(actor, name)
        self.reset( target=target, speed=speed)
        
    def reset( self, target:Degrees|None=None, speed:DegreesPerSecond|None = None ):
        """Reset the servo movement parameters."""
        if target is not None: self.target = target
        if speed is not None: self.speed = speed
        if self.actor.currentBehavior is self:
            self.actor.setCurrentBehavior(self, reset=True)

    def activate( self, target:Degrees|None=None, speed:DegreesPerSecond|None = None, context:EvaluationContext|None=None ) -> "ServoMovement":
        self.reset( target=target,speed=speed)
        self.actor.currentBehavior = self
        return self

        
    def enter(self, context):
        self.actor._servo.moveTo( self.target, self.speed, context )
    
    def exit(self, context):
        pass
    
    
    
class ServoDoor(Door):
    """_summary_

    Args:
        Door (_type_): _description_
    """
    _servo:LocalServo
    closedPosition:Degrees = 45.0
    openPosition:Degrees = 90.0
    defaultSpeed:TimeInSeconds = 5.0 # time required to move from closed to open
    
    #opening: ServoMovement
    #closing: ServoMovement
    #closed: ServoMovement
    #opened: ServoMovement
    #moving: ServoMovement
    #stopped: ServoMovement
    
    @property
    def span(self) -> Degrees:
        return  self.openPosition - self.closedPosition 
    
    def convertSpeed(self, speed:TimeInSeconds) -> DegreesPerSecond:
            (speed/self.span)
    
    @property
    def openRatio(self):
            return (self._servo.lastSetAngle - self.closedPosition) - self.span
            
    def __init__(self,
            servo:LocalServo,
            closedPosition:Degrees|None = None,
            openPosition:Degrees|None = None,
            defaultSpeed:TimeInSeconds|None = None,
            name:str|None = None, 
            main:"LumensalisCP.Main.Manager.MainManager"|None = None
        ):
        super().__init__(name, main)
        self._servo = servo
        
        if closedPosition is not None: self.closedPosition = closedPosition
        if openPosition is not None: self.openPosition = openPosition
        if defaultSpeed is not None: self.defaultSpeed = defaultSpeed
        
        self.opening = ServoMovement(self, "Opening" )
        self.closing = ServoMovement(self, "Closing")
        self.opened = ServoMovement(self, "Opened")
        self.closed = ServoMovement(self, "Closed")
        self.moving = ServoMovement(self, "Moving")
        self.stopped = ServoMovement(self, "Stopped")
        
        
    def open(self, speed:TimeInSeconds|None = None, context:EvaluationContext|None=None) -> Behavior:
        return self.opening.activate(speed=speed, context=context)
        
    def close(self, speed:TimeInSeconds|None = None, context:EvaluationContext|None=None) -> Behavior:
        return self.closing.activate(speed=speed, context=context)

    def stop(self, context:EvaluationContext|None=None) -> None:
        return self.stopped.activate(target=self._servo.lastSetAngle, context=context)

            
    def addOpenTrigger( self, Input): pass
    
    def _moveCompleted(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        self.dbgOut("ServoDoor move completed")