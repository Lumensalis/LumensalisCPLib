
import adafruit_vl53l0x # type: ignore # pylint: disable=import-error

from LumensalisCP.I2C.common import *

#############################################################################

class VL53L0XInput(I2CInputSource):
    def __init__( self, **kwargs ):
        super().__init__(**kwargs)
        self._range:int = 8192
        
    def getDerivedValue(self, context:EvaluationContext) -> int:
        if context.debugEvaluate:
            self.infoOut( "getDerivedValue = %r", self._range )
        return self._range
    
    def _setRange( self, r:int, context:EvaluationContext) -> bool:
        if self._range != r:
            self._range = r
            #self.dbgOut( "MPR121Input = %s", touched )
            self.updateValue( context )
            return True
        return False
            

#############################################################################

class VL53L0X(I2CDevice):
    
    def __init__(self, *args, updateInterval=0.1, **kwds ):
        I2CDevice.__init__( self, *args, updateInterval=updateInterval, **kwds )
        self.__readMode = 'startMeasurement'
        self._sensor = adafruit_vl53l0x.VL53L0X(self.i2c, io_timeout_s=1.0)
        self.__range = VL53L0XInput(target=self,name="range")

    @property
    def range(self) -> VL53L0XInput: 
        """ range (in mm) to the nearest object detected by the VL53L0X sensor."""
        return self.__range
    
    
    def derivedUpdateDevice(self, context:EvaluationContext) -> bool:
        if self.__readMode is None or self.__readMode  == 'startMeasurement':
            self._sensor.do_range_measurement()
            self.__readMode = "measuring"
        elif self.__readMode == "measuring":
            if self._sensor.data_ready:
                r = self._sensor.range
                self.__readMode = "startMeasurement"
                #self.dbgOut( "ranger range = %s", range )
                return self.__range._setRange(r, context=context) # pylint: disable=protected-access

        return False
