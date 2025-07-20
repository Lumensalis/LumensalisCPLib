
import adafruit_aw9523 # pylint: disable=import-error # type: ignore

from LumensalisCP.I2C.common import *

class AW9523Input(I2CInputSource):
    def __init__( self, parent:"AW9523", pin:int, name:Optional[str]=None, **kwargs ):
        name = name or f"{parent.name}_I{pin}"
        super().__init__(parent,name=name,**kwargs)
        self.io = adafruit_aw9523.DigitalInOut( pin, parent.aw9523 )
        self.io.switch_to_input()
        
        self.__pin = pin
        self.__mask = 1 << pin
        self._value:bool = False

    @property 
    def pin(self): return self.__pin

    def getDerivedValue(self, context:EvaluationContext) -> bool: # pylint: disable=unused-argument
        return self._value

    def _setFromInputs( self, inputsValue, context:EvaluationContext):
        value = (inputsValue & self.__mask) != 0
        #self.dbgOut( "_setFromInputs  %X / %r",  inputsValue, value )
        
        if self._value != value:
            self._value = value
            if self.enableDbgOut: self.dbgOut( "INPUT %s = %s (%X & %X)", self.__pin, value, inputsValue, self.__mask )
            self.updateValue( context )    
    


class AW9523(I2CDevice):
    AW9523_PINS = 16
    
    def __init__(self, **kwds ):
        updateKWDefaults( kwds,
            updateInterval = 0.1,
        )
        super().__init__(name="AW9523",**kwds)
        self.aw9523 = adafruit_aw9523.AW9523( i2c_bus=self.i2c )
        
        self.__ios:List[AW9523Input|None] = [None] * AW9523.AW9523_PINS
        self.__lastInputs = 0
        #self.__updates = 0
        #self.__changes = 0


    def addInput(self, pin:int, name:Optional[str]=None, **kwds ):
        ensure( isinstance(pin, int) and pin >= 0 and pin < AW9523.AW9523_PINS, "invalid pin %r", pin )
        ensure( self.__ios[pin] is None, "pin %r already used", pin )
        io = AW9523Input( self, pin, name=name,**kwds )
        self.__ios[pin] = io
        return io
        
    @property
    def inputs(self): return list(filter( lambda i: i is not None and isinstance(i,AW9523Input), self.__ios ))
    
    @property
    def lastInputs(self): return self.__lastInputs


    def derivedUpdateTarget(self, context:EvaluationContext):
        inputValues = self.aw9523.inputs
        self.__updates += 1
        if self.__lastInputs != inputValues:
            self.__lastInputs = inputValues
            self.__changes += 1
            if self.enableDbgOut: self.dbgOut( "AW9523 = %X",  inputValues )
            
            for inp in self.__ios:
                if inp is not None:
                    inp._setFromInputs( inputValues, context )
