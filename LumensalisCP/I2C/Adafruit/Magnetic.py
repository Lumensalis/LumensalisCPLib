

from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from ..I2CDevice import I2CDevice, I2CInputSource, UpdateContext
import math

import adafruit_tlv493d


class TLV493DInput(I2CInputSource):
    def __init__( self, mx:int = None, **kwargs ):
        super().__init__(**kwargs)
        self.__mx  = mx
        self._lastReading = 0

    def getDerivedValue(self, context:UpdateContext) -> bool:
        return self._lastReading 
    
    def _setValue( self, readingTuple, context:UpdateContext):
        reading = readingTuple[self.__mx]
        if self._lastReading != reading:
            self._lastReading = reading
            self.dbgOut( "TLV493DInput = %s", reading )
            self.updateValue( context )
            

class I2CSimpleInput(I2CInputSource):
    def __init__( self,value=None, **kwargs ):
        super().__init__(**kwargs)
        self.__simpleValue = value


    def getDerivedValue(self, context:UpdateContext) -> bool:
        return self.__simpleValue 
    
    def _setValue( self, value, context:UpdateContext):
        if self.__simpleValue != value:
            self.__simpleValue = value
            self.dbgOut( "value  = %s", value )
            self.updateValue( context )
            
            
class TLV493D(I2CDevice,adafruit_tlv493d.TLV493D):
    
    def __init__(self, *args, **kwds ):
        updateKWDefaults( kwds,
            updateInterval = 0.1,
        )
        
        I2CDevice.__init__( self, *args,**kwds )
        adafruit_tlv493d.TLV493D.__init__(self, self.i2c)
        self.__lastReading:Tuple[int,int,int]  = [0,0,0]
        
        self.__inputs:List[TLV493DInput] = [
            TLV493DInput( mx=0,name="x" ),
            TLV493DInput( mx=0,name="y" ),
            TLV493DInput( mx=0,name="z" )
        ]
        
        self.__distance = I2CSimpleInput(name="distance")
        
    @property
    def x(self) -> TLV493DInput: return self.__inputs[0]
    @property
    def y(self) -> TLV493DInput: return self.__inputs[1]
    @property
    def z(self) -> TLV493DInput: return self.__inputs[2]
    @property
    def distance(self) -> I2CSimpleInput: return self.__distance
    
    def derivedUpdateTarget(self, context:UpdateContext):
        reading = self.magnetic
        if self.__lastReading != reading:
            # self.dbgOut( "MPR121 = %X" % allTouched )
            self.__lastReading != reading

            
            crTotal = 0
            for ix, input in enumerate(self.__inputs):
                input._setValue( reading, context )
                crTotal +=  reading[ix] *  reading[ix]
                
            distance = math.sqrt( crTotal )
            self.__distance._setValue( distance, context )

            self.dbgOut( "new reading : %8.1f [ %5d %5d %5d ] ", distance, *reading )