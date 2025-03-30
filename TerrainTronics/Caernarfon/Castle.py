
import time
import board
import microcontroller
import busio
import pwmio
import adafruit_motor.servo
import neopixel
import pulseio, adafruit_irremote
import TerrainTronics.D1MiniBoardBase
from LumensalisCP.Main.Expressions import InputSource, OutputTarget, EvaluationContext, UpdateContext
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.common import *

from LumensalisCP.Triggers.Timer import PeriodicTimer
from LumensalisCP.CPTyping import *
import math

# import time, board, microcontroller, busio, pwmio, adafruit_motor.servo, neopixel, TerrainTronics.D1MiniBoardBase


class CaernarfonServo( adafruit_motor.servo.Servo, OutputTarget ):
    def __init__(self, pwm=None, name:str=None, 
                 movePeriod:TimeInSeconds = 0.05,
                 moveSpeed:DegreesPerSecond = 60.0,
                 angleMin:Degrees = 10,
                 angleMax:Degrees = 135,
                 castle:"CaernarfonCastle" = None,
                 **kwds ):
        adafruit_motor.servo.Servo.__init__(self, pwm, **kwds)
        OutputTarget.__init__(self, name=name)

        self.__moveTimer = PeriodicTimer( movePeriod, manager=castle.main.timers, name=f"{self.name}_timer" )
        self.__moveTimer.addAction( self._updateMove )
        self.__moveSpeed:DegreesPerSecond = moveSpeed
        self.__moveTarget:Degrees|None = None
        self.__moveTimeAtStart:TimeInSeconds|None = None
        self.__moveAngleStart:Degrees|None = None
        self.__moveSpan:Degrees|None = None
        self.__moving = False
        self.__angleMin = angleMin
        self.__angleMax = angleMax
        self.__lastSetAngle = self.rangedAngle( self.angle or 90.0 )
        


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
            self.angle = None
            
    def set( self, angle:Degrees|None, context:EvaluationContext=None ):
        if self.__moving:
            self.stop(turnOff=False)
        self.__set( angle, context )

    def __set( self, angle:Degrees|None, context:EvaluationContext=None ):
        if angle is not None:
            angle = self.rangedAngle( angle )
        self.__lastSetAngle = angle
        self.angle = angle
        
    def moveTo( self, angle:Degrees, speed:DegreesPerSecond|None=None, context:EvaluationContext=None ):
        assert angle is not None
        span =  angle - self.__lastSetAngle
        if span == 0:
            self.stop()
            return
        
        if speed is not None:
            self.__moveSpeed = speed
        
        self.__moving = True
        self.__moveTarget = self.rangedAngle( angle )
        self.__moveAngleStart = self.__lastSetAngle
        self.__moveSpan = angle - self.__lastSetAngle
        self.__moveTimeAtStart = context.when if context is not None else self.__moveTimer.manager.main.when
            
        self.dbgOut( f"moveTo {self.__moveTarget}d from {self.__moveAngleStart}d / {self.__moveTimeAtStart :0.3f}s at {self.__moveSpeed}dPs, span {self.__moveSpan}" )
        self.__moveTimer.start()

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
        self.dbgOut( f"angleOffset={angleOffset:0.1f}d after {elapsed:0.3f}s, dt={driveTime} mr = {moveRatio}   )  "  )
        
        newTarget = self.__moveAngleStart + angleOffset

        if self.__moveSpan > 0.0:
            finished = newTarget > self.__moveTarget
        else:
            finished = newTarget < self.__moveTarget
                
        if finished:
            self.dbgOut( f"servo {self.name} move to {self.__moveTarget} complete, elapsed={elapsed} newTarget={newTarget} distance={angleOffset}" )
            newTarget = self.__moveTarget
            self.set( newTarget, context=context )
        else:
            self.dbgOut( f"_updateMove( {when:0.3f} ) elapsed={elapsed:0.3f} from {self.__lastSetAngle:0.1f}d + {angleOffset:.1f}d to {newTarget:0.1f}d at {self.__moveSpeed:0.1f}dPs, {angleOffset:0.1f}d from {self.__moveAngleStart:0.1f}d towards {self.__moveTarget:0.1f}d" )
            self.__set( newTarget )

    @property
    def moveSpeed(self): return self.__moveSpeed

class CaernarfonNeoPixel( neopixel.NeoPixel):
    def __init__(self, *args, refreshRate:int = 0, main:MainManager = None, **kwds):
        super().__init__(*args,**kwds)
        self._main = main
        self._changesSinceRefresh = 0
        self._refreshRate = refreshRate
        self._latestRefresh = 0
        
    def _set_item(
        self, index: int, r: int, g: int, b: int, w: int
    ):  # pylint: disable=too-many-locals,too-many-branches,too-many-arguments
        if index < 0:
            index += len(self)
        if index >= self._pixels or index < 0:
            raise IndexError
        offset = self._offset + (index * self._bpp)
        contentsBefore = self._pre_brightness_buffer[offset,  self._bpp]
        super()._set_item( index, r, g, b, w )
        contentsAfter = self._pre_brightness_buffer[offset,  self._bpp]
        if contentsAfter != contentsBefore:
            self._changesSinceRefresh += 1

    def refresh(self):
        if self._refreshRate:
            elapsed = self._main.when - self._latestRefresh
            if elapsed > self._refreshRate:
                self.show()

    def show(self):
        super().show()
        self._latestRefresh = self._main.when
        
        
class LCP_IRrecv(Debuggable):
    
    def __init__(self, pin, codenames:MainManager = {} ):
        super().__init__()
        self.pulseIn = pulseio.PulseIn(pin, maxlen=120, idle_state=True)
        self.decoder = adafruit_irremote.GenericDecode()
        self.__callbacksByCode:Mapping[int,Callable] = {}
        self.__unhandledCallback = self._unhandled
        self.codenames = codenames
        
        

    def handleRawCode(self, rawCode ):
        code = 0
        for byte in rawCode:
            code = (code *256) + byte
            
            
        cb = self.__callbacksByCode.get(code,None) # self.__unhandledCallback)
        if cb is not None:
            if 1: self.dbgOut( f"calling callback for code {"%x"%code}, cb={cb}")
            cb()
        else:
            self._unhandled(code, rawCode)
        
    def _unhandled(self, code, rawCode ):
        self.errOut( f"unhandled remote code: 0x{"%x"%code} from {rawCode}" )
        

    def setUnhandledCallback( self, cb:Callable ):
        self.__unhandledCallback = cb
        
    def addCallbackForCode(self, code:int|str, cb:Callable ):
        if type(code) is str:
            code = self.codenames[code]

        dictAddUnique(self.__callbacksByCode, code, cb )

    def onCode( self, code:int|str=None, action:Callable = None ):
        assert code is not None
        assert action is not None
        self.addCallbackForCode( code, action )
        
    def check( self ):
        pulses = self.decoder.read_pulses(self.pulseIn, blocking=False)
        if pulses is None: return
        # print("Heard", len(pulses), "Pulses:", pulses)
        try:
            code = self.decoder.decode_bits(pulses)
            
            self.handleRawCode( code )
        except adafruit_irremote.IRNECRepeatException:  # unusual short code!
            self.warnOut("NEC repeat!")
        except (
            adafruit_irremote.IRDecodeException,
            adafruit_irremote.FailedToDecode,
        ) as e:  # failed to decode
            self.warnOut("Failed to decode: %s", e.args)

    
def onIRCode( ir: LCP_IRrecv, code:int|str ):
        
    def on2( callable ):
        ir.addCallbackForCode( code, callable )
        return callable
    return on2

class CaernarfonCastle(TerrainTronics.D1MiniBoardBase.D1MiniBoardBase):
    def __init__(self, *args, name=None, **kwds ):
        name = name or "Caernarfon"
        super().__init__( *args, name=name, **kwds )
        c = self.config
        c.updateDefaultOptions( 
                neoPixelPin = c.D3,
                neoPixelCount = 1,
                neoPixelOrder = neopixel.GRB,
                neoPixelBrightness = 0.2,
                servos = 0,
                servo1pin =  c.D6,
                servo2pin =  c.D7,
                servo3pin =  c.D8,
            )
        self._irRemote = None
        self.initI2C()
        self.pixels = CaernarfonNeoPixel(
            c.neoPixelPin, c.neoPixelCount, main = self.main, refreshRate=0.05, brightness=c.neoPixelBrightness, auto_write=False, pixel_order=c.neoPixelOrder
        )
        self.servos = [ None, None, None ]
        if False and c.servos > 0:
            self.initServo(1)
            if c.servos > 1:
                self.initServo(2)
                if c.servos > 2:
                    self.initServo(3)
        
    @property
    def servo1(self) -> CaernarfonServo:
        return  self.servos[0] 
    
    servo2 = property( lambda self: self.servos[1] )
    servo3 = property( lambda self: self.servos[2] )

    def addIrRemote(self, codenames:Mapping|None = None) -> LCP_IRrecv:
        assert self._irRemote is None
        codenames = codenames or {
            "CH-": 0xffa25d,
            "CH": 0xff629d,
            "CH+": 0xffe21d,
            "PREV": 0xff22dd,
            "NEXT": 0xFF02FD,
            "PLAY": 0xffc23d,
            "VOL-": 0xffe01f,
            "VOL+": 0xffa857,
        }
        self._irRemote = LCP_IRrecv( self.D5.actualPin, codenames=codenames )
        return self._irRemote
    
    def analogInput( self, name, pin ):
        return self.main.addInput( name, pin )
    
    def initServo( self, servoN:int, name:str = None, duty_cycle:int = 2 ** 15, frequency=50, **kwds) -> CaernarfonServo:
        assert( self.servos[servoN-1] is None )
        pin = self.config.option('servo{}pin'.format(servoN))
        name = name or f"servo{servoN}"
        pwm = pwmio.PWMOut( pin, duty_cycle=duty_cycle, frequency=frequency)
        servo = CaernarfonServo(pwm,name, castle=self, **kwds)
        self.servos[servoN-1] = servo
        return servo
