
import time
import board
import microcontroller
import busio
import pwmio
import adafruit_motor.servo
import neopixel
import TerrainTronics.D1MiniBoardBase
from LumensalisCP.Main.Expressions import InputSource, OutputTarget, EvaluationContext

from LumensalisCP.CPTyping import *

# import time, board, microcontroller, busio, pwmio, adafruit_motor.servo, neopixel, TerrainTronics.D1MiniBoardBase

class CaernarfonServo( adafruit_motor.servo.Servo, OutputTarget ):
    def __init__(self, pwm=None, name:str=None, **kwds ):
        adafruit_motor.servo.Servo.__init__(self, pwm, **kwds)
        OutputTarget.__init__(self, name=name)

    def set( self, value:Any, context:EvaluationContext ):
        self.angle = max( 0, min(value,180))
        
        
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
        self.initI2C()
        self.pixels = neopixel.NeoPixel(
            c.neoPixelPin, c.neoPixelCount, brightness=c.neoPixelBrightness, auto_write=False, pixel_order=c.neoPixelOrder
        )
        self.servos = [ None, None, None ]
        if c.servos > 0:
            self.initServo(1)
            if c.servos > 1:
                self.initServo(2)
                if c.servos > 2:
                    self.initServo(3)
        
    servo1 = property( lambda self: self.servos[0] )
    servo2 = property( lambda self: self.servos[1] )
    servo3 = property( lambda self: self.servos[2] )

    def analogInput( self, name, pin ):
        return self.main.addInput( name, pin )
    
    def initServo( self, servoN:int, name:str = None, duty_cycle:int = 2 ** 15, frequency=50, ):
        assert( self.servos[servoN-1] is None )
        pin = self.config.option('servo{}pin'.format(servoN))
        name = name or f"servo{servoN}"
        pwm = pwmio.PWMOut( pin, duty_cycle=duty_cycle, frequency=frequency)
        servo = CaernarfonServo(pwm,name)
        self.servos[servoN-1] = servo
