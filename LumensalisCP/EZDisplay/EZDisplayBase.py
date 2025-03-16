from ..I2C.I2CTarget import I2CTarget

import displayio
from i2cdisplaybus import I2CDisplayBus

class EZDisplayBase(object):
    def __init__(self, displayWidth = 128, displayHeight = 64, **kwds ):
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight 

class EZI2cDisplayIoBase(I2CTarget, EZDisplayBase):
    def __init__(self, displayWidth = 128, displayHeight = 64, i2c=None, device_address=0x3c, reset=None, **kwds ):
        I2CTarget.__init__( self, i2c=i2c, device_address=device_address, reset=reset, **kwds )
        EZDisplayBase.__init__( self, displayWidth = displayWidth, displayHeight = displayHeight, **kwds )
        self.displayBus = I2CDisplayBus(self.i2c, device_address=device_address, reset=reset ) 
        
        self._initDisplayInstance()
        
        # print(f"EZI2cDisplayIoBase  set canvas...")
        self.canvas = displayio.Group()
        self.root_group = self.canvas

    def _initDisplayInstance(self):
        pass
    
    