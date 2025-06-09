
# This is a factory for adding Adafruit Stemma/QT modules

from ..I2CFactory import I2CFactory, I2CFactoryAddArgs
import LumensalisCP.I2C.Adafruit
from LumensalisCP.common import *

class AdafruitFactory(I2CFactory):
    
    def addQTRotaryEncoder(self, *args, **kwds:I2CFactoryAddArgs ):
        updateKWDefaults( kwds, main=self.main )
        from .QTRotaryEncoder import QtRotary
        return QtRotary( *args, **kwds )

    def addNunchuk( self, *args, **kwds ):
        updateKWDefaults( kwds, main=self.main )
        from .Nunchuk import Nunchuk
        return Nunchuk( *args, **kwds )

    def addMPR121( self, *args, **kwds ) -> "LumensalisCP.I2C.Adafruit.MPR121.MPR121":
        updateKWDefaults( kwds, main=self.main )
        from .MPR121 import MPR121
        return MPR121( *args, **kwds )
    

    def addTLV493D( self, *args, **kwds ):
        updateKWDefaults( kwds, main=self.main )
        from .Magnetic import TLV493D
        return TLV493D( *args, **kwds )
    
    def addAW9523( self, *args, **kwds ):
        updateKWDefaults( kwds, main=self.main )
        from .AW9523 import AW9523
        return AW9523( *args, **kwds )
    
    def addPCA9685( self, *args, **kwds ):
        updateKWDefaults( kwds, main=self.main )
        from .PCA9685 import PCA9685
        return PCA9685( *args, **kwds )    