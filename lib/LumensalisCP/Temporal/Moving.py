# type: ignore
from LumensalisCP.IOContext import *
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Triggers.Timer import PeriodicTimer
import math

class Moving( NamedOutputTarget, Refreshable ):
    """_summary_
        Provides an output which can move over
        time between zero and one
    Args:
        NamedOutputTarget (_type_): _description_
        Refreshable (_type_): _description_
    """
    
    target:ZeroToOne|Evaluatable # destination value
    moving:bool # true if still moving towards destination
    
    @property
    def speed(self) -> TimeInSeconds|Evaluatable:
        # time required for full range move
        raise NotImplemented
        
    def __init__(self, name:Optional[str]=None, 
                 speed:TimeInSeconds = 1.0,
                 target:ZeroToOne = 0.0,
                 main:MainManager = None,
                 **kwds ):
        #adafruit_motor.servo.Servo.__init__(self, pwm, **kwds)
        NamedOutputTarget.__init__(self, name=name)

        self.speed:TimeInSeconds = moveSpeed
        self.__moveTarget:ZeroToOne|None = None
        
        
        self.__moveTimeAtStart:TimeInSeconds|None = None
        self.__moveAngleStart:Degrees|None = None
        ## self.__moveSpan:Degrees|None = None
        self.__moveCompleteCB:Callable|None = None
        self.__onStopCB:Callable|None = None
        self.__moving = False
        self.__angleMin = angleMin
        self.__angleMax = angleMax
        self.__latestValue = 0.0

    
    @property
    def latestValue(self) -> ZeroToOne: return self.__latestValue
    
    def stop(self  ):
        if self.__moving:
            self.__moveTarget = None
            self.__moveSpan = None
            self.__moveTimeAtStart = None
            self.__moveAngleStart = None
            self.__moveTimer.stop()
        
    
    def set( self, value:ZeroToOne|None, context:Optional[EvaluationContext]=None ):
        if self.__moving:
            self.stop()
        self.__set( value, context )

    def __set( self, value:ZeroToOne|None, context:Optional[EvaluationContext]=None ):
        if angle is not None:
            angle = self.rangedAngle( angle )
            self.__lastSetAngle = angle
        self.__servo.angle = angle
        
    def moveTo( self, value:ZeroToOne, speed:Optional[TimeInSeconds]=None, context:Optional[EvaluationContext]=None ):
        assert value is not None
        span =  angle - self.__lastSetAngle
        if span == 0:
            self.stop()
            return
        
        if speed is not None:
            self.__moveSpeed = speed
        if self.__moving and self.__moveCompleteCB is not None:
            self.__moveCompleteCB()
            
        self.__moving = True
        self.__moveTarget = self.rangedAngle( angle )
        self.__moveAngleStart = self.__lastSetAngle
        self.__moveSpan = angle - self.__lastSetAngle
        self.__moveTimeAtStart = context.when if context is not None else self.__moveTimer.manager.main.when
            
        self.enableDbgOut and self.dbgOut( f"moveTo {self.__moveTarget}d from {self.__moveAngleStart}d / {self.__moveTimeAtStart :0.3f}s at {self.__moveSpeed}dPs, span {self.__moveSpan}" )
        self.__moveTimer.start()

    def onStop( self, callable:Callable ):
        self.__onStopCB = callable

    def onMoveComplete( self, callable:Callable ):
        self.__moveCompleteCB = callable

    def _updateMove(self, when:Optional[TimeInSeconds]=None, context:Optional[EvaluationContext]=None):
        assert when is not None

        finished = False
        elapsed = when - self.__moveTimeAtStart
        if elapsed <= 0:
            self.warnOut( "unexpected elapsed {}", elapsed )
            return
        
        driveTime =  math.fabs( self.__moveSpan ) / self.__moveSpeed
        moveRatio = elapsed / driveTime
        angleOffset = moveRatio * self.__moveSpan
        self.enableDbgOut and self.dbgOut( f"angleOffset={angleOffset:0.1f}d after {elapsed:0.3f}s, dt={driveTime} mr = {moveRatio}   )  "  )
        
        newTarget = self.__moveAngleStart + angleOffset

        if self.__moveSpan > 0.0:
            finished = newTarget > self.__moveTarget
        else:
            finished = newTarget < self.__moveTarget
                
        if finished:
            self.enableDbgOut and self.dbgOut( f"servo {self.name} move to {self.__moveTarget} complete, elapsed={elapsed} newTarget={newTarget} distance={angleOffset}" )
            newTarget = self.__moveTarget
            self.set( newTarget, context=context )
            if self.__moveCompleteCB is not None:
                self.__moveCompleteCB()
        else:
            self.enableDbgOut and self.dbgOut( f"_updateMove( {when:0.3f} ) elapsed={elapsed:0.3f} from {self.__lastSetAngle:0.1f}d + {angleOffset:.1f}d to {newTarget:0.1f}d at {self.__moveSpeed:0.1f}dPs, {angleOffset:0.1f}d from {self.__moveAngleStart:0.1f}d towards {self.__moveTarget:0.1f}d" )
            self.__set( newTarget )

    @property
    def moveSpeed(self): return self.__moveSpeed
