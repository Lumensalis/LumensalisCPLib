
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


class I2CFactory(object):
    def __init__(self, main=None):
        assert main is not None
        self.main = main
    
    def addDisplay_SSD1306(self, **kwds:Unpack[Display_SSD1306.KWDS] ):
        from LumensalisCP.I2C.Generic.Display_SSD1306 import Display_SSD1306
        return Display_SSD1306( main=self.main, **kwds )

    def addDisplayIO_SSD1306(self, **kwds:Unpack[DisplayIO_SSD1306.KWDS] ):
        from LumensalisCP.I2C.Generic.DisplayIO_SSD1306 import DisplayIO_SSD1306
        return DisplayIO_SSD1306( main=self.main, **kwds )

    def addVL530lx(self, **kwds: Unpack[VL53L0X.KWDS] ) -> VL53L0X: # pylint: disable=used-before-assignment
        """ add a VL53L0X distance sensor """
        from LumensalisCP.I2C.Generic.VL530lx import VL53L0X
        return VL53L0X( main=self.main, **kwds )
