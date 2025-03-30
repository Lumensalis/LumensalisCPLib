
# This is a factory for adding Adafruit Stemma/QT modules

from ..I2CFactory import I2CFactory

class SparkfunI2CFactory(I2CFactory):
    
    def addQTRotaryEncoder(self, *args, **kwds ):
        from .QTRotaryEncoder import QtRotary
        return QtRotary( *args, **kwds )

    def addNunchuk( self, *args, **kwds ):
        from .Nunchuk import Nunchuk
        return Nunchuk( *args, **kwds )
