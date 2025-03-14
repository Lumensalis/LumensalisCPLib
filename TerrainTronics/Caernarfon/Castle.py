
import time
import board
import microcontroller
import busio
import pwmio
import adafruit_motor.servo
import neopixel
import TerrainTronics.BoardBase

# import time, board, microcontroller, busio, pwmio, adafruit_motor.servo, neopixel, TerrainTronics.BoardBase

class CaernarfonCastle(TerrainTronics.BoardBase.BoardBase):
    def __init__(self, *args, **kwds ):
        super().__init__( *args, **kwds )
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
        
    def initServo( self, servoN:int, duty_cycle:int = 2 ** 15, frequency=50, ):
        assert( self.servos[servoN-1] is None )
        pin = self.config.option('servo{}pin'.format(servoN))
        pwm = pwmio.PWMOut( pin, duty_cycle=duty_cycle, frequency=frequency)
        servo = adafruit_motor.servo.Servo(pwm)
        self.servos[servoN-1] = servo
