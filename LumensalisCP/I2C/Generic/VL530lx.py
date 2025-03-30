import adafruit_vl53l0x

from ..I2CTarget import I2CTarget
import simpleio


class VL53L0X(I2CTarget,adafruit_vl53l0x.VL53L0X):
    
    def __init__(self, *args, **kwds ):
        I2CTarget.__init__( self, *args,**kwds )
        adafruit_vl53l0x.VL53L0X.__init__(self, self.i2c)
        
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