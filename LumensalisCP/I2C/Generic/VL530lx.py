
from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from ..I2CTarget import I2CTarget, I2CInputSource, UpdateContext

import adafruit_vl53l0x
import simpleio

class VL53L0XInput(I2CInputSource):
    def __init__( self, **kwargs ):
        super().__init__(**kwargs)
        self._range = 8192
        
    def getDerivedValue(self, context:UpdateContext) -> bool:
        return self._range
    
    def _setRange( self, range, context:UpdateContext):
        if self._range != range:
            self._range = range
            #self.dbgOut( "MPR121Input = %s", touched )
            self.updateValue( context )
            

                    
                    
class VL53L0X(I2CTarget):
    
    def __init__(self, *args, updateInterval=0.1, **kwds ):
        I2CTarget.__init__( self, *args, updateInterval=updateInterval, **kwds )
        
        self._sensor = adafruit_vl53l0x.VL53L0X(self.i2c, io_timeout_s=1.0)
        self.__readMode = 'startMeasurement'
        self.__range = VL53L0XInput(target=self,name="range")

    @property
    def range(self): return self.__range
    
    def derivedUpdateTarget(self, context:UpdateContext):
        if self.__readMode is None or self.__readMode  == 'startMeasurement':
            self._sensor.do_range_measurement()
            self.__readMode = "measuring"
        elif self.__readMode == "measuring":
            if self._sensor.data_ready:
                range = self._sensor.range
                self.__readMode = "startMeasurement"
                self.dbgOut( "ranger range = %s", range )
                self.__range._setRange(range, context=context)
