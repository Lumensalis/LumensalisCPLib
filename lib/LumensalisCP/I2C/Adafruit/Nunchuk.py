import adafruit_nunchuk

from LumensalisCP.I2C.I2CDevice import  I2CDevice
import simpleio


class Nunchuk(I2CDevice,adafruit_nunchuk.Nunchuk):
    
    def __init__(self, *args, **kwds ):
        I2CDevice.__init__( self, *args,**kwds )
        adafruit_nunchuk.Nunchuk.__init__(self, self.i2c)
        
        self.scaleXmin = -1.0
        self.scaleXmax = 1.0
        
        self.scaleYmin = -1.0
        self.scaleYmax = 1.0
        
    
    def readScaledJoystick(self):
        j = self.joystick 
        return (
            simpleio.map_range( j[0], 0, 255, self.scaleXmin, self.scaleXmax ),
            simpleio.map_range( j[1], 0, 255, self.scaleYmin, self.scaleYmax )
        )
    scaledJoystick = property( lambda self: self.readScaledJoystick() )