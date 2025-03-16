
from .I2CTarget import I2CTarget

import displayio
import adafruit_displayio_ssd1306
from i2cdisplaybus import I2CDisplayBus
from adafruit_displayio_ssd1306 import SSD1306 as SSD1306_DIO

class DisplayIO_SSD1306(I2CTarget,SSD1306_DIO):
    
    def __init__(self, displayWidth = 128, displayHeight = 64, i2c=None, device_address=0x3c, **kwds ):
        I2CTarget.__init__( self, i2c=i2c,**kwds )
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight 
        print( f"i2c is a {type(self.i2c)} / {dir(self.i2c)}")
        
        
        self.displayBus = I2CDisplayBus(self.i2c, device_address=device_address ) # , reset=None ) 
        SSD1306_DIO.__init__( self, self.displayBus, width=self.displayWidth, height=self.displayHeight )
        self.canvas = displayio.Group()
        self.root_group = self.canvas
        
        if 0:
            self.color_bitmap = displayio.Bitmap(displayWidth, displayHeight, 1)
            self.color_palette = displayio.Palette(1)
            self.color_palette[0] = 0xFFFFFF # White
            self.bg_sprite = displayio.TileGrid(self.color_bitmap, pixel_shader=self.color_palette, x=0, y=0)
            self.canvas.append(self.bg_sprite)
        
