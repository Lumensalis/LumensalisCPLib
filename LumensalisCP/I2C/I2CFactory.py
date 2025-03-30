
# There are several objectives met by these factory classes
#
# by moving the I2CTarget creation into dedicated class APIs,
# it keeps the Main.Manager class from getting more cluttered
#
# it removes the need for the user to import the class themselves
#
# by importing the supporting modules _within_ the add/create calls,
# it avoids loading the supporting code until it's actually used

from LumensalisCP.CPTyping import *
from .I2CTarget import I2CTargetInitArgs

class I2CFactoryAddArgs(I2CTargetInitArgs):
    pass

class I2CFactory(object):
    def __init__(self, main=None):
        assert main is not None
        self.main = main
    
        
    def addDisplay_SSD1306(self, *args, **kwds:I2CFactoryAddArgs ):
        from .Generic.Display_SSD1306 import Display_SSD1306
        return Display_SSD1306( *args, **kwds )

    def addDisplayIO_SSD1306(self, *args, **kwds:I2CFactoryAddArgs ):
        from .Generic.DisplayIO_SSD1306 import DisplayIO_SSD1306
        return DisplayIO_SSD1306( *args, **kwds )

    def addVL530lx(self, *args, **kwds:I2CFactoryAddArgs ):
        from .Generic.VL530lx import VL53L0X
        return VL53L0X( *args, main=self.main, **kwds )
