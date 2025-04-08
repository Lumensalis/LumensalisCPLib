
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