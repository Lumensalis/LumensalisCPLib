import pwmio
import neopixel
import TerrainTronics.D1MiniBoardBase
from LumensalisCP.common import *

from LumensalisCP.Lights.NeoPixels import NeoPixelSource

from LumensalisCP.Gadgets.IrRemote import LCP_IRrecv, onIRCode
from LumensalisCP.Gadgets.Servos import LocalServo

from LumensalisCP.Triggers.Timer import PeriodicTimer
from LumensalisCP.CPTyping import *
import math


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
        self.__pixels:NeoPixelSource = NeoPixelSource(
            c.neoPixelPin, c.neoPixelCount, main = self.main, refreshRate=0.05, brightness=c.neoPixelBrightness, auto_write=False, pixel_order=c.neoPixelOrder
        )
        self.servos = [ None, None, None ]
     
    @property
    def servo1(self) -> LocalServo:
        return  self.servos[0] 
    
    @property
    def pixels(self) -> NeoPixelSource: return self.__pixels
        
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
        self._irRemote = LCP_IRrecv( self.D5.actualPin, codenames=codenames, main=self.main )
        return self._irRemote
    
    def analogInput( self, name, pin ):
        return self.main.addInput( name, pin )
    
    def initServo( self, servoN:int, name:str = None, duty_cycle:int = 2 ** 15, frequency=50, **kwds) -> LocalServo:
        assert( self.servos[servoN-1] is None )
        pin = self.config.option('servo{}pin'.format(servoN))
        name = name or f"servo{servoN}"
        pwm = pwmio.PWMOut( pin, duty_cycle=duty_cycle, frequency=frequency)
        servo = LocalServo(pwm,name, main=self.main, **kwds)
        self.servos[servoN-1] = servo
        return servo
