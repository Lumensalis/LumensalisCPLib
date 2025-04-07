

from LumensalisCP.EZDisplay.EZDisplayBase import EZI2cDisplayIoBase

import displayio
from adafruit_displayio_ssd1306 import SSD1306 as SSD1306_DIO

class DisplayIO_SSD1306( EZI2cDisplayIoBase, SSD1306_DIO ):
    
    def __init__(self, displayWidth=None, displayHeight=None, **kwds ):
        EZI2cDisplayIoBase.__init__( self, displayWidth=displayWidth, displayHeight=displayHeight, **kwds )
        # print( f"i2c is a {type(self.i2c)} / {dir(self.i2c)}")

        #SSD1306_DIO.__init__( self, self.displayBus, width=self.displayWidth, height=self.displayHeight )
        
        
        if 0:
            self.color_bitmap = displayio.Bitmap(displayWidth, displayHeight, 1)
            self.color_palette = displayio.Palette(1)
            self.color_palette[0] = 0xFFFFFF # White
            self.bg_sprite = displayio.TileGrid(self.color_bitmap, pixel_shader=self.color_palette, x=0, y=0)
            self.canvas.append(self.bg_sprite)
        
    def _initDisplayInstance(self):
        kwargs = dict( width=self.displayWidth, height=self.displayHeight )
        print(f"DisplayIO_SSD1306  _initDisplayInstance... {kwargs}")
        
        SSD1306_DIO.__init__( self, self.displayBus, **kwargs )
