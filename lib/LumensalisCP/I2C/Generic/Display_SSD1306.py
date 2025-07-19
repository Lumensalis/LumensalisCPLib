from LumensalisCP.I2C.I2CDevice import  I2CDevice

from adafruit_ssd1306 import SSD1306_I2C


class Display_SSD1306(I2CDevice,SSD1306_I2C):
    
    def __init__(self, displayWidth = 128, displayHeight = 64, i2c=None, **kwds ):
        I2CDevice.__init__( self, i2c=i2c,**kwds )
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight 
        SSD1306_I2C.__init__( self, self.displayWidth, self.displayHeight, self.i2c )