import busio
from LumensalisCP.Controllers.ConfigurableBase import ControllerConfigurableChildBase
from LumensalisCP.IOContext import * # InputSource, NamedOutputTarget, EvaluationContext, Refreshable, UpdateContext

from digitalio import DigitalInOut, Direction
from analogio import AnalogIn
import microcontroller

# from LumensalisCP.CPTyping import Any, Callable, Generator, List, Mapping, Tuple

class PinHolder( object ):
    def __init__(self, pin:"PinProxy" ):
        self.pinProxy = pin
        self.actualPinId = getattr( pin.board.config.pins, pin.name )

class DigitalPinHolder( PinHolder ):
    def __init__(self, pin:"PinProxy" ):
        super().__init__( pin = pin )
        self.pin = DigitalInOut( self.actualPinId )

class AnalogInputPinProxy( InputSource, PinHolder ):
    def __init__(self, name:str, pin:"PinProxy" ):
        InputSource.__init__(self,name=name)
        
        PinHolder.__init__(self, pin=pin)
        self.pin = AnalogIn( self.actualPinId )

        
    def getDerivedValue(self, context:EvaluationContext) -> Any:
        return self.pin.value        

class DigitalInputPinProxy( InputSource, DigitalPinHolder ):
    def __init__(self, name:str, pin:"PinProxy" ):
        InputSource.__init__(self,name=name)
        DigitalPinHolder.__init__(self, pin=pin)
        self.pin.direction = Direction.INPUT
        
    def getDerivedValue(self, context:EvaluationContext) -> Any:
        return self.pin.value
        
class DigitalOutputPinProxy( NamedOutputTarget, DigitalPinHolder ):
    def __init__(self, name:str, pin:"PinProxy" ):
        NamedOutputTarget.__init__(self, name=name)
        DigitalPinHolder.__init__(self, pin=pin)
        self.pin.direction = Direction.OUTPUT
        
    def set( self, value:Any, context:EvaluationContext ): 
        self.pin.value = value


class PinProxy(CountedInstance):
    def __init__( self, name:str, board:"D1MiniBoardBase" ):
        super().__init__()
        self._name = name
        self._board = board

    @property 
    def actualPin(self) -> microcontroller.Pin:
        return getattr( self._board.config.pins, self._name )
    
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
    