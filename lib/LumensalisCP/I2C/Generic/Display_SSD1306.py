from adafruit_ssd1306 import SSD1306_I2C # type: ignore # pylint: disable=import-error

from LumensalisCP.I2C.common import  *


class Display_SSD1306(I2CDevice,SSD1306_I2C):
    class KWDS(I2CDevice.KWDS):
        displayWidth: NotRequired[int]
        displayHeight: NotRequired[int]
        
    def __init__(self, main, displayWidth = 128, displayHeight = 64, **kwds:Unpack[I2CDevice.KWDS] ):
        I2CDevice.__init__( self, main, **kwds )
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight 
        SSD1306_I2C.__init__( self, self.displayWidth, self.displayHeight, self.i2c )
        
    def derivedUpdateDevice(self, context:EvaluationContext):
        return False    
