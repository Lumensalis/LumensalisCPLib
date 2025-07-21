
# This is a factory for adding Adafruit Stemma/QT modules

from ..I2CFactory import I2CFactory, I2CFactoryAddArgs
from .QTRotaryEncoder import QtRotary
from .Nunchuk import Nunchuk
from .MPR121 import MPR121
from .Magnetic import TLV493D
from .AW9523 import AW9523
from .PCA9685 import PCA9685
from .VCNL4040 import VCNL4040
from LumensalisCP.common import *

_UnpackedFactoryArgs = Unpack[I2CFactoryAddArgs]| dict[str, Any]
class AdafruitFactory(I2CFactory):
    
    def addQTRotaryEncoder(self, *args:Any, **kwds:_UnpackedFactoryArgs ) -> QtRotary: ...

    def addNunchuk( self, *args:Any , **kwds:_UnpackedFactoryArgs ) -> Nunchuk: ...

    def addMPR121( self, *args:Any, **kwds:_UnpackedFactoryArgs ) -> MPR121: ...

    def addTLV493D( self, *args:Any, **kwds:_UnpackedFactoryArgs ) -> TLV493D: ...
    
    def addAW9523( self, *args:Any, **kwds:_UnpackedFactoryArgs ) -> AW9523: ...

    def addPCA9685( self, *args:Any, **kwds:_UnpackedFactoryArgs ) -> PCA9685: ...

    def addVCNL4040( self, *args:Any, **kwds:_UnpackedFactoryArgs ) -> VCNL4040: ...
