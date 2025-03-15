
from .I2CTarget import I2CTarget

# import displayio
# import terminalio
# from adafruit_display_text import label
# from i2cdisplaybus import I2CDisplayBus
# import adafruit_displayio_ssd1306
# displayio.release_displays()


from adafruit_ssd1306 import SSD1306_I2C


class Display_SSD1306(I2CTarget,SSD1306_I2C):
    
    def __init__(self, displayWidth = 128, displayHeight = 64, i2c=None, **kwds ):
        I2CTarget.__init__( self, i2c=i2c,**kwds )
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight 
        SSD1306_I2C.__init__( self, self.displayWidth, self.displayHeight, self.i2c )