from __future__ import annotations
# This is a factory for adding Adafruit Stemma/QT modules

# TODO: tighten up type hints and linting

# type: ignore

#import LumensalisCP.I2C.Adafruit
from LumensalisCP.common import *
from LumensalisCP.I2C.I2CFactory import I2CFactory

# pylint: disable=unused-import,import-error,reimported,import-outside-toplevel

if TYPE_CHECKING:
    from LumensalisCP.I2C.Adafruit.QTRotaryEncoder import QtRotary
    from LumensalisCP.I2C.Adafruit.Nunchuk import Nunchuk
    from LumensalisCP.I2C.Adafruit.MPR121 import MPR121
    from LumensalisCP.I2C.Adafruit.VCNL4040 import VCNL4040
    from LumensalisCP.I2C.Adafruit.Magnetic import TLV493D
    from LumensalisCP.I2C.Adafruit.AW9523 import AW9523
    from LumensalisCP.I2C.Adafruit.PCA9685 import PCA9685
    
    
class AdafruitFactory(I2CFactory):
    
    def addQTRotaryEncoder(self, **kwds:Unpack[QtRotary.KWDS] ) -> QtRotary:
        """Add a QTRotaryEncoder."""
        from LumensalisCP.I2C.Adafruit.QTRotaryEncoder import QtRotary
        return QtRotary( main=self.main, **kwds )

    def addNunchuk( self, **kwds:Unpack[Nunchuk.KWDS] ) -> Nunchuk:
        """Add a Nunchuk controller."""
        from LumensalisCP.I2C.Adafruit.Nunchuk import Nunchuk
        return Nunchuk( main=self.main, **kwds )

    def addMPR121( self, **kwds:Unpack[MPR121.KWDS] ) -> MPR121:
        """Add a MPR121 capacitive touch sensor."""
        from LumensalisCP.I2C.Adafruit.MPR121 import MPR121
        return MPR121(  main=self.main, **kwds )

    def addVCNL4040( self, **kwds:Unpack[VCNL4040.KWDS] ) -> VCNL4040:
        """Add a VCNL4040 proximity and ambient light sensor."""
        from LumensalisCP.I2C.Adafruit.VCNL4040 import VCNL4040
        return VCNL4040(  main=self.main, **kwds )

    def addTLV493D( self, **kwds:Unpack[TLV493D.KWDS] ) -> TLV493D:
        """Add a TLV493D 3D magnetic sensor."""
        from LumensalisCP.I2C.Adafruit.Magnetic import TLV493D
        return TLV493D(  main=self.main, **kwds )
    
    def addAW9523( self, **kwds :Unpack[AW9523.KWDS] ) -> AW9523:
        """Add an AW9523 GPIO expander with LED driver."""
        from LumensalisCP.I2C.Adafruit.AW9523 import AW9523
        return AW9523(  main=self.main, **kwds )

    def addPCA9685( self, **kwds:Unpack[PCA9685.KWDS] ) -> PCA9685:
        """Add a PCA9685 PWM driver."""
        from LumensalisCP.I2C.Adafruit.PCA9685 import PCA9685
        return PCA9685(  main=self.main, **kwds )
