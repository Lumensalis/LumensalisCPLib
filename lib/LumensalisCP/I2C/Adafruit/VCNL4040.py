
from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from ..I2CDevice import I2CDevice, I2CInputSource, EvaluationContext

import adafruit_vcnl4040 # type: ignore


class VCNL4040ConfigDescriptor:
    def __init__(self, name:str='???'):
        self.attrName = name
    def __set_name__(self, owner, name):
        print( f"{self.__class__.__name__}.__set_name__ {name}" )
        self.attrName = name

    def __get__(self, obj:'VCNL4040', objtype=None):
        value = getattr(obj.vcnl4040, self.attrName)
        #logging.info('Accessing %r giving %r', self.public_name, value)
        return value

    def __set__(self, obj:'VCNL4040', value):
        if obj.dbgOut: obj.dbgOut( 'Updating %r to %r', self.attrName, value )
        setattr(obj.vcnl4040, self.attrName, value)

                
class VCNL4040Input(I2CInputSource):
    def __init__( self, parent:"VCNL4040", attr:str, name:Optional[str]=None, **kwargs ):
        super().__init__(parent,name=name,**kwargs)
        self.attr = attr
        self.vcnl4040 = parent.vcnl4040
        self._value:Any =  getattr( self.vcnl4040, self.attr ) 

    def getDerivedValue(self, context:EvaluationContext) -> bool:
        return self._value
    
    def _setFromHW( self, context:EvaluationContext):
        value = getattr( self.vcnl4040, self.attr ) 
        
        if self._value != value:
            self._value = value
            #if self.enableDbgOut: self.dbgOut( "NEW VALUE %s cycle=%s",  value, context.updateIndex )
            self.updateValue( context )    
        # elif self.enableDbgOut: self.dbgOut( "unchanged %s cycle=%s",  value, context.updateIndex )
        
        
class VCNL4040ReadableDescriptor:

    def __init__(self, name:str):
        self.name = name
        self.inputName = "_i_" + name
        
    def __set_name__(self, owner, name):
        print( f"__set_name__ {name}" )
        assert False
        self.name = name

    def __get__(self, obj:'VCNL4040', objtype=None):
        try:
            return  getattr(obj.vcnl4040, self.inputName)
        except:
            pass
        value = VCNL4040Input(obj,self.name)
        setattr(obj.vcnl4040, self.inputName, value)
        obj.__ios.append(value)
        return value

    def __set__(self, obj:'VCNL4040', value) -> None:
        obj.raiseException( '%r is read only', self.name )
        #setattr(obj.vcnl4040, self.public_name, value)        

class VCNL4040(I2CDevice):
    
    def __init__(self, **kwds ):
        updateKWDefaults( kwds,
            updateInterval = 0.1,
        )
        super().__init__(**kwds)
        self.vcnl4040 = adafruit_vcnl4040.VCNL4040( i2c=self.i2c )
        
        self.__ios:List[VCNL4040Input] = []
        self.__lastInputs = 0
        self.__updates = 0
        self.__changes = 0

    light_high_threshold  = VCNL4040ConfigDescriptor('light_high_threshold')
    light_integration_time = VCNL4040ConfigDescriptor('light_integration_time')
    light_shutdown = VCNL4040ConfigDescriptor('light_shutdown')
    proximity_bits = VCNL4040ConfigDescriptor('proximity_bits')
    proximity_low_threshold = VCNL4040ConfigDescriptor('proximity_low_threshold')
    proximity_high_threshold = VCNL4040ConfigDescriptor('proximity_high_threshold')
    proximity_integration_time = VCNL4040ConfigDescriptor('proximity_integration_time')
    proximity_interrupt = VCNL4040ConfigDescriptor('proximity_interrupt')
    proximity_shutdown = VCNL4040ConfigDescriptor('proximity_shutdown')
    white_shutdown =  VCNL4040ConfigDescriptor('white_shutdown')

    def __addInput(self, attr:str ):
        io = VCNL4040Input(self,'light')
        setattr( self, f"_{attr}", io )
        self.__ios.append(io)
        return io
    
    light = VCNL4040ReadableDescriptor('light')
    lux = VCNL4040ReadableDescriptor('lux')
    proximity = VCNL4040ReadableDescriptor('proximity')
    white = VCNL4040ReadableDescriptor('white')
    
    def derivedUpdateTarget(self, context:EvaluationContext):
        if self.enableDbgOut: self.dbgOut( "reading %r ios", len(self.__ios))
        for input in self.__ios:
            input._setFromHW( context )
