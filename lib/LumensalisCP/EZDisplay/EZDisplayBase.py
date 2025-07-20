from ..I2C.I2CDevice import I2CDevice

import displayio, terminalio
from i2cdisplaybus import I2CDisplayBus
import adafruit_display_text.label  # pyright: ignore[reportMissingImports]

class EZDisplayBase(object):
    def __init__(self, displayWidth = 128, displayHeight = 64, **kwds ):
        self.displayWidth = displayWidth or 128
        self.displayHeight = displayHeight or 64


class EZDisplayElement(object):
    def __init__(self):
        pass
    
class EZI2cDisplayIoBase(I2CDevice, EZDisplayBase):
    def __init__(self, displayWidth = 128, displayHeight = 64, i2c=None, device_address=0x3c, reset=None, **kwds ):
        I2CDevice.__init__( self, i2c=i2c, address=device_address, **kwds )
        EZDisplayBase.__init__( self, displayWidth = displayWidth, displayHeight = displayHeight, **kwds )
        self.displayBus = I2CDisplayBus(self.i2c, device_address=device_address, reset=reset ) 
        
        self._initDisplayInstance()
        
        # print(f"EZI2cDisplayIoBase  set canvas...")
        self.canvas = displayio.Group()
        self.root_group = self.canvas

    def addBitmap( self, filename ):
        bitmap = displayio.OnDiskBitmap(open(filename, "rb"))
        image = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
        self.canvas.append(image) 
        return image
       
    def addText( self, text:str, x:int|None, y:int|None ):
        x = x if x is not None else 0
        y = y if y is not None else 0
        
        label =  adafruit_display_text.label.Label(
            terminalio.FONT, text=text, color=0xFFFFFF, x=x, y=y )
               
        self.canvas.append( label )
        return label
    
        
    def _initDisplayInstance(self): raise NotImplementedError

