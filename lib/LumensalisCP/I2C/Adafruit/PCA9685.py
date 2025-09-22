
from re import U
from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false
from LumensalisCP.I2C.I2CDevice import  I2CDevice, I2CInputSource, I2COutputTarget, UpdateContext

import adafruit_pca9685

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager

    from LumensalisCP.Eval.EvaluationContext import EvaluationContext

class PCA9685Output(I2COutputTarget):
    def __init__( self, parent:"PCA9685", pin:int, 
                 channel:adafruit_pca9685.PWMChannel, 
                 name:Optional[str]=None,  
                 **kwargs:Any ) -> None:
        
        name = name or f"{parent.name}_I{pin}"
        super().__init__(name=name,**kwargs)
        self.__pin = pin
        #ensure( channel is not None, "PCA9685Output requires channel" )
        self.__channel = channel
        self.__value:ZeroToOne = 0.0

    @property 
    def pin(self): return self.__pin
    
    
    def set( self, value:Any, context:EvaluationContext ):
        v = withinZeroToOne( value )
        if self.__value != v:
            self.__value = v
            self.__dc = int( v * 65535 )
            self.__channel.duty_cycle = self.__dc

    @property
    def channel(self): return self.__channel
    
    @property
    def value(self): return self.__value


class PCA9685(I2CDevice):
    PCA9685_PINS = 16
    
    def __init__(self, **kwds:Unpack[I2CDevice.KWDS] ):
        #updateKWDefaults( kwds,
        #    frequency = 50,
        #    # refreshRate = 0.1,
        #)
        frequency = kwds.pop("frequency", 50.0 )
        kwds.setdefault('temporaryName', "PCA9685")
        super().__init__(**kwds)
        self.pca9685 = adafruit_pca9685.PCA9685( i2c_bus=self.i2c )
        assert isinstance(frequency, float)
        self.pca9685.frequency = frequency
        self.__ios:List[PCA9685Output|None] = [None] * PCA9685.PCA9685_PINS

    def addOutput(self, pin:int, **kwds:Any ):
        ensure( type(pin) is int and pin >= 0 and pin < PCA9685.PCA9685_PINS, "invalid pin %r", pin )
        ensure( self.__ios[pin] is None, "pin %r already used", pin )
        io = PCA9685Output( self, pin, channel = self.pca9685.channels[pin], **kwds  )
        self.__ios[pin] = io
        return io

    def __getitem__(self, index:int) -> PCA9685Output:
        assert index >= 0 and index < PCA9685.PCA9685_PINS 
        rv = self.__ios[index]
        assert rv is not None
        return rv


