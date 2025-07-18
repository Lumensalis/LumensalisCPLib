
from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from ..I2CDevice import I2CDevice, I2CInputSource, EvaluationContext

import adafruit_vcnl4040

class VCNL4040Input(I2CInputSource):
    def __init__( self, parent:"VCNL4040", attr:str, name:Optional[str]=None, **kwargs ):
        super().__init__(parent,name=name,**kwargs)
        self.attr = attr
        self.vcnl4040 = parent.vcnl4040
        self._value:Any = None

    def getDerivedValue(self, context:EvaluationContext) -> bool:
        return self._value

    def _setFromHW( self, context:EvaluationContext):
        value = getattr( self.vcnl4040, self.attr ) 
        
        if self._value != value:
            self._value = value
            if self.enableDbgOut: self.dbgOut( "NEW VALUE %s cycle=%s",  value, context.updateIndex )
            self.updateValue( context )    
        # elif self.enableDbgOut: self.dbgOut( "unchanged %s cycle=%s",  value, context.updateIndex )
        
        

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

    def __addInput(self, attr:str ):
        io = VCNL4040Input(self,'light')
        setattr( self, f"_{attr}", io )
        self.__ios.append(io)
        return io
        
    _light: VCNL4040Input
    @property
    def light(self) -> VCNL4040Input:
        try: return self._light
        except: return self.__addInput( 'light' )

    _lux: VCNL4040Input
    @property
    def lux(self) -> VCNL4040Input:
        try: return self._lux
        except: return self.__addInput( 'lux' )
    
    _proximity: VCNL4040Input
    @property
    def proximity(self) -> VCNL4040Input:
        try: return self._proximity
        except: return self.__addInput( 'proximity' )

    _white: VCNL4040Input
    @property
    def white(self) -> VCNL4040Input:
        try: return self._white
        except: return self.__addInput( 'white' )

    def derivedUpdateTarget(self, context:EvaluationContext):
        if self.enableDbgOut: self.dbgOut( "reading %r ios", len(self.__ios))
        for input in self.__ios:
            input._setFromHW( context )

