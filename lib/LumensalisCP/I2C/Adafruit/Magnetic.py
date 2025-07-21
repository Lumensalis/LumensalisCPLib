

import adafruit_tlv493d # type: ignore # pylint: disable=import-error

from LumensalisCP.I2C.common import *


class TLV493DInput(I2CInputSource):
    def __init__( self, device:I2CDevice, mx:int, name:str ):
        super().__init__(device,name=name )
        self.__mx  = mx
        self._lastReading:int = 0

    def getDerivedValue(self, context:EvaluationContext) -> int: # pylint: disable=unused-argument
        return self._lastReading 
    
    def _setValue( self, readingTuple:tuple[int,int,int], context:EvaluationContext):
        reading = readingTuple[self.__mx]
        if self._lastReading != reading:
            self._lastReading = reading
            if self.enableDbgOut: self.dbgOut( "TLV493DInput = %s", reading )
            self.updateValue( context )
            


class I2CSimpleInput(I2CInputSource):
    def __init__( self, device:I2CDevice, value:Any=None, **kwargs:Unpack[I2CInputSource.KWDS] ):
        super().__init__(device, **kwargs)
        self.__simpleValue:Any = value


    def getDerivedValue(self, context:EvaluationContext) -> bool: # pylint: disable=unused-argument
        return self.__simpleValue 
    
    def _setValue( self, value:Any, context:EvaluationContext): # pylint: disable=unused-argument
        if self.__simpleValue != value:
            self.__simpleValue = value
            if self.enableDbgOut: self.dbgOut( "value  = %s", value )
            self.updateValue( context )
            return True

class TLV493D(I2CDevice,adafruit_tlv493d.TLV493D):
    DEFAULT_UPDATE_INTERVAL = TimeInSeconds(0.1)
    
    def __init__(self, **kwds:Unpack[I2CDevice.KWDS] ):
                
        I2CDevice.__init__( self, **kwds ) 
        adafruit_tlv493d.TLV493D.__init__(self, self.i2c)
        self.__lastReading:Tuple[int,int,int]  = (0,0,0)
        
        self.__inputs:List[TLV493DInput] = [
            TLV493DInput( self, mx=0,name="x" ),
            TLV493DInput( self,mx=0,name="y" ),
            TLV493DInput( self, mx=0,name="z" )
        ]
        
        self.__distance = I2CSimpleInput( self, 0, name="distance")
        
    @property
    def x(self) -> TLV493DInput: return self.__inputs[0]
    @property
    def y(self) -> TLV493DInput: return self.__inputs[1]
    @property
    def z(self) -> TLV493DInput: return self.__inputs[2]
    @property
    def distance(self) -> I2CSimpleInput: return self.__distance
    
    @property 
    def lastReading(self) -> tuple[int,int,int]:
        return self.__lastReading
    
    def derivedUpdateDevice(self, context:EvaluationContext):
        reading = self.magnetic
        if self.__lastReading != reading:
            # self.dbgOut( "MPR121 = %X" % allTouched )
            self.__lastReading = reading

            
            crTotal = 0
            for ix, inputSource in enumerate(self.__inputs):
                inputSource._setValue( reading, context ) # pylint: disable=protected-access
                crTotal +=  reading[ix] *  reading[ix]
                
            distance = math.sqrt( crTotal )
            self.__distance._setValue( distance, context ) # pylint: disable=protected-access

            if self.enableDbgOut: self.dbgOut( "new reading : %8.1f [ %5d %5d %5d ] ", distance, *reading )
            return True
