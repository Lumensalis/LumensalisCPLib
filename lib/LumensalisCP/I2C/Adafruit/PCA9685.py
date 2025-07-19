
from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from ..I2CDevice import I2CDevice, I2CInputSource, I2COutputTarget, UpdateContext

import adafruit_pca9685

class PCA9685Output(I2COutputTarget):
    def __init__( self, parent:"PCA9685", pin:int = None, name:Optional[str]=None,  channel:adafruit_pca9685.PWMChannel = None, **kwargs ):
        name = name or f"{parent.name}_I{pin}"
        super().__init__(name=name,**kwargs)
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
    
    def __init__(self, **kwds ):
        #updateKWDefaults( kwds,
        #    frequency = 50,
        #    # updateInterval = 0.1,
        #)
        frequency = kwds.pop("frequency", 50 )
        super().__init__(name="PCA9685",**kwds)
        self.pca9685 = adafruit_pca9685.PCA9685( i2c_bus=self.i2c )
        self.pca9685.frequency = frequency
        self.__ios:List[PCA9685Output|None] = [None] * PCA9685.PCA9685_PINS

    def addOutput(self, pin:int, name:Optional[str]=None, **kwds ):
        ensure( type(pin) is int and pin >= 0 and pin < PCA9685.PCA9685_PINS, "invalid pin %r", pin )
        ensure( self.__ios[pin] is None, "pin %r already used", pin )
        io = PCA9685Output( self, pin, name=name, channel = self.pca9685.channels[pin], **kwds  )
        self.__ios[pin] = io
        return io

    def __getitem__(self, index):
        ensure( index >= 0 and index < PCA9685.PCA9685_PINS and (rv := self.pca9685) is not None )
        return rv


