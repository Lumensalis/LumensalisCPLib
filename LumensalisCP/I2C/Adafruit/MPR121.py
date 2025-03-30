
from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from ..I2CTarget import I2CTarget, I2CInputSource, UpdateContext

import adafruit_mpr121

class MPR121Input(I2CInputSource):
    def __init__( self, pin:int = None, **kwargs ):
        super().__init__(**kwargs)
        self.__pin = pin
        self.__mask = 1 << pin
        self._touched:bool = False

    def getDerivedValue(self, context:UpdateContext) -> bool:
        return self._touched
    
    def _setTouched( self, allTouched, context:UpdateContext):
        touched = (allTouched & self.__mask) != 0
        if self._touched != touched:
            self._touched = touched
            self.dbgOut( "MPR121Input = %s", touched )
            self.updateValue( context )
            
MPR121_PINS = 12
class MPR121(I2CTarget,adafruit_mpr121.MPR121):
    
    def __init__(self, *args, **kwds ):
        updateKWDefaults( kwds,
            updateInterval = 0.1,
        )
        
        I2CTarget.__init__( self, *args,**kwds )
        adafruit_mpr121.MPR121.__init__(self, self.i2c)
        self.__lastTouched:int = 0
        self.__inputs:List[MPR121Input|None] = [None] * MPR121_PINS

    def derivedUpdateTarget(self, context:UpdateContext):
        allTouched = self.touched()
        if self.__lastTouched != allTouched:
            # self.dbgOut( "MPR121 = %X" % allTouched )
            self.__lastTouched != allTouched
            
        for input in self.__inputs:
            if input is not None:
                input._setTouched( allTouched, context )
    
    def addInput( self, pin:int=None, name:str = None ):
        assert pin >= 0 and pin < len(self.__inputs)
        input = self.__inputs[pin]
    
        if input is not None:
            assert name == input.name
        else:
            input = MPR121Input( pin=pin, name=name, target=self)
            self.__inputs[pin] = input
            
        return input
