from .I2CFactory import I2CFactory
from .Adafruit.AdafruitI2CFactory import AdafruitFactory

class I2CFactory(object):
    def __init__(self, main=None):
        self.main = main
    
        
    def addDisplay_SSD1306(self, *args, **kwds ):
        from .Display_SSD1306 import Display_SSD1306
        return Display_SSD1306( *args, **kwds )

    def addDisplayIO_SSD1306(self, *args, **kwds ):
        from .DisplayIO_SSD1306 import DisplayIO_SSD1306
        return DisplayIO_SSD1306( *args, **kwds )
