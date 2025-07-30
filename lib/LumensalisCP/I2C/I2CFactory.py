
# There are several objectives met by these factory classes
#
# by moving the I2CDevice creation into dedicated class APIs,
# it keeps the Main.Manager class from getting more cluttered
#
# it removes the need for the user to import the class themselves
#
# by importing the supporting modules _within_ the add/create calls,
# it avoids loading the supporting code until it's actually used

# pylint: disable=unused-import,import-error,reimported,import-outside-toplevel
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

from LumensalisCP.CPTyping import *
from LumensalisCP.I2C.I2CDevice import  I2CDevice
# pylint: disable=unused-import,import-error,reimported,import-outside-toplevel,used-before-assignment
        
if TYPE_CHECKING:
    from LumensalisCP.I2C.Generic.Display_SSD1306 import Display_SSD1306
    from LumensalisCP.I2C.Generic.DisplayIO_SSD1306 import DisplayIO_SSD1306
    from LumensalisCP.I2C.Generic.VL530lx import VL53L0X
    from LumensalisCP.Main.Manager import MainManager

#############################################################################

class I2CFactory(object):
    def __init__(self, main:MainManager|None=None):
        assert main is not None
        self.main:MainManager = main
    
    def addDisplay_SSD1306(self, **kwds:Unpack[Display_SSD1306.KWDS] ) -> Display_SSD1306:
        """Add an SSD1306 display"""
        from LumensalisCP.I2C.Generic.Display_SSD1306 import Display_SSD1306
        kwds.setdefault('main', self.main)
        return Display_SSD1306( **kwds )

    def addDisplayIO_SSD1306(self, **kwds:Unpack[DisplayIO_SSD1306.KWDS] ) -> DisplayIO_SSD1306:
        """Add an SSD1306 display (using DisplayIO)"""
        from LumensalisCP.I2C.Generic.DisplayIO_SSD1306 import DisplayIO_SSD1306
        kwds.setdefault('main', self.main)
        return DisplayIO_SSD1306( **kwds )

    def addVL530lx(self, **kwds: Unpack[VL53L0X.KWDS] ) -> VL53L0X: # pylint: disable=used-before-assignment
        """ add a VL53L0X distance sensor """
        from LumensalisCP.I2C.Generic.VL530lx import VL53L0X
        kwds.setdefault('main', self.main)
        return VL53L0X( **kwds )

#############################################################################
