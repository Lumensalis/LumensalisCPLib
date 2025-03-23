
import board
import busio
from LumensalisCP.Controllers.ConfigurableBase import ControllerConfigurableChildBase
from LumensalisCP.Main.Expressions import InputSource, OutputTarget, EvaluationContext
from digitalio import DigitalInOut, Direction
from analogio import AnalogIn

from LumensalisCP.CPTyping import Any, Callable, Generator, List, Mapping, Tuple

class PinHolder( object ):
    def __init__(self, pin:"D1MiniPinProxy" ):
        self.pinProxy = pin
        self.actualPinId = getattr( pin.board.config.pins, pin.name )

class DigitalPinHolder( PinHolder ):
    def __init__(self, pin:"D1MiniPinProxy" ):
        super().__init__( pin = pin )
        self.pin = DigitalInOut( self.actualPinId )

class AnalogInputPinProxy( InputSource, PinHolder ):
    def __init__(self, name:str, pin:"D1MiniPinProxy" ):
        InputSource.__init__(self,name=name)
        PinHolder.__init__(self, pin=pin)
        self.pin = AnalogIn( self.actualPinId )

        
    def getDerivedValue(self, context:EvaluationContext) -> Any:
        return self.pin.value        

class DigitalInputPinProxy( InputSource, DigitalPinHolder ):
    def __init__(self, name:str, pin:"D1MiniPinProxy" ):
        InputSource.__init__(self,name=name)
        DigitalPinHolder.__init__(self, pin=pin)
        self.pin.direction = Direction.INPUT
        
    def getDerivedValue(self, context:EvaluationContext) -> Any:
        return self.pin.value
        
class DigitalOutputPinProxy( OutputTarget, DigitalPinHolder ):
    def __init__(self, name:str, pin:"D1MiniPinProxy" ):
        OutputTarget.__init__(self, name=name)
        DigitalPinHolder.__init__(self, pin=pin)
        self.pin.direction = Direction.OUTPUT
        
    def set( self, value:Any, context:EvaluationContext ): 
        self.pin.value = value

class D1MiniPinProxy(object):
    def __init__( self, name:str, board:"D1MiniBoardBase" ):
        self._name = name
        self._board = board

    @property
    def name(self) -> str: return self._name
    
    @property
    def board(self) -> "D1MiniBoardBase": return self._board
    
    def addAnalogInput( self, name:str ) -> AnalogInputPinProxy:
        return AnalogInputPinProxy( name=name, pin=self )

    def addInput( self, name:str ) -> DigitalInputPinProxy:
        return DigitalInputPinProxy( name=name, pin=self )

    def addOutput( self, name:str ) -> DigitalOutputPinProxy:
        return DigitalOutputPinProxy( name=name, pin=self )
    
class D1MiniBoardBase(ControllerConfigurableChildBase):
    def __init__(self, **kwds ):
        super().__init__( **kwds )
        print( f"D1MiniBoardBase.__init__( {kwds})")
        assert self.main is not None
        
        self.TX = D1MiniPinProxy( 'TX', self )
        self.RX = D1MiniPinProxy( 'RX', self )
        self.SDA= D1MiniPinProxy( 'SDA', self )
        self.SCL= D1MiniPinProxy( 'SCL', self )
        self.D1= D1MiniPinProxy( 'D1', self )
        self.D2= D1MiniPinProxy( 'D2', self )
        self.D3= D1MiniPinProxy( 'D3', self )
        self.D4= D1MiniPinProxy( 'D4', self )
        self.D5= D1MiniPinProxy( 'D5', self )
        self.D6= D1MiniPinProxy( 'D6', self )
        self.D7= D1MiniPinProxy( 'D7', self )
        self.D8= D1MiniPinProxy( 'D8', self )
        self.A0= D1MiniPinProxy( 'A0', self )

    def dbgOut(self, fmt, *args, **kwds): 
        if 0:
            print( fmt.format(*args,**kwds) )

    def initI2C(self): 
        i2c = self.config.option('i2c')
        sdaPin = self.config.SDA
        sclPin = self.config.SCL
        
        if i2c is None:
            if sdaPin is None and sclPin is None:
                i2c = board.I2C()
            else:
                self.dbgOut( "initializing busio.I2C, scl={}, sda={}", sclPin, sdaPin )
                i2c =  busio.I2C( sdaPin, sclPin ) 

        assert( i2c is not None )
        
        self.i2c = i2c
        self.sdaPin = sdaPin
        self.sclPin = sclPin
        
    def scanI2C(self):
        print( "scanning i2c\n")
                
        while not self.i2c.try_lock():
            pass

        try:
            #while True:
            print(
                "I2C addresses found:",
                [hex(device_address) for device_address in self.i2c.scan()],
                )
            #   time.sleep(2)

        finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
            self.i2c.unlock()

        print( "i2c scan complete\n")

