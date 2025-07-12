import adafruit_motor.servo
import pwmio
from LumensalisCP.IOContext import *
#from LumensalisCP.Main.Expressions import NamedOutputTarget, EvaluationContext, UpdateContext
#from LumensalisCP.Inputs import InputSource
from LumensalisCP.Main.Manager import MainManager
#from LumensalisCP.common import *

from LumensalisCP.Triggers.Timer import PeriodicTimer
#from LumensalisCP.CPTyping import *
import math

class LocalServo( 
                      #adafruit_motor.servo.Servo,
                      NamedOutputTarget ):
    def __init__(self, pwm:pwmio.PWMOut=None, name:str=None, 
                 movePeriod:TimeInSeconds = 0.05,
                 moveSpeed:DegreesPerSecond = 60.0,
                 angleMin:Degrees = 10,
                 angleMax:Degrees = 135,
                 main:MainManager = None,
                 **kwds ):
        #adafruit_motor.servo.Servo.__init__(self, pwm, **kwds)
        NamedOutputTarget.__init__(self, name=name)

        self.__servo = adafruit_motor.servo.Servo( pwm, **kwds)
        self.__moveTimer = PeriodicTimer( movePeriod, manager=main.timers, name=f"{self.name}_timer" )
        self.__moveTimer.addAction( self._updateMove )
        self.__moveSpeed:DegreesPerSecond = moveSpeed
        self.__moveTarget:Degrees|None = None
        self.__moveTimeAtStart:TimeInSeconds|None = None
        self.__moveAngleStart:Degrees|None = None
        self.__moveSpan:Degrees|None = None
        self.__moveCompleteCB:Callable|None = None
        self.__onStopCB:Callable|None = None
        self.__moving = False
        self.__angleMin = angleMin
        self.__angleMax = angleMax
        self.__lastSetAngle = self.rangedAngle( self.__servo.angle or 90.0 )

    @property
    def _moveTimer(self) -> PeriodicTimer: return self.__moveTimer
    
    @property
    def lastSetAngle(self): return self.__lastSetAngle
    
    def rangedAngle( self, angle:Degrees ):
        if angle < self.__angleMin: return self.__angleMin
        if angle > self.__angleMax: return self.__angleMax
        return angle
        
        
    def stop(self, turnOff = True ):
        if self.__moving:
            self.__moveTarget = None
            self.__moveSpan = None
            self.__moveTimeAtStart = None
            self.__moveAngleStart = None
            self.__moveTimer.stop()
        if turnOff:
            self.__servo.angle = None
    
    
    def set( self, angle:Degrees|None, context:EvaluationContext=None ):
        if self.__moving:
            self.stop(turnOff=False)
        self.__set( angle, context )

    def __set( self, angle:Degrees|None, context:EvaluationContext=None ):
        if angle is not None:
            angle = self.rangedAngle( angle )
            self.__lastSetAngle = angle
        self.__servo.angle = angle
        
    def moveTo( self, angle:Degrees, speed:DegreesPerSecond|None=None, context:EvaluationContext=None ):
        assert angle is not None
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

    def _updateMove(self, when:TimeInSeconds=None, context:EvaluationContext=None):
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
