
# This is a factory for adding Adafruit Stemma/QT modules

from ..I2CFactory import I2CFactory, I2CFactoryAddArgs
from .QTRotaryEncoder import QtRotary
from .Nunchuk import Nunchuk
from .MPR121 import MPR121
from .Magnetic import TLV493D
from .AW9523 import AW9523
from .PCA9685 import PCA9685
from .VCNL4040 import VCNL4040

class AdafruitFactory(I2CFactory):
    
    def addQTRotaryEncoder(self, *args, **kwds:I2CFactoryAddArgs ) -> QtRotary: ...

    def addNunchuk( self, *args, **kwds:I2CFactoryAddArgs ) -> Nunchuk: ...

    def addMPR121( self, *args, **kwds:I2CFactoryAddArgs ) -> MPR121: ...

    def addTLV493D( self, *args, **kwds:I2CFactoryAddArgs ) -> TLV493D: ...
    
    def addAW9523( self, *args, **kwds:I2CFactoryAddArgs ) -> AW9523: ...

    def addPCA9685( self, *args, **kwds ) -> PCA9685: ...
    
    def addVCNL4040( self, *args, **kwds ) -> VCNL4040: ...
