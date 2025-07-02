
import busio
from LumensalisCP.Controllers.ConfigurableBase import ControllerConfigurableChildBase

from LumensalisCP.IOContext import NamedOutputTarget, EvaluationContext, InputSource, UpdateContext
from LumensalisCP.Main.Updates import Refreshable

from LumensalisCP.Shields.Pins import PinHolder, PinProxy
from LumensalisCP.Shields.Base import ShieldBase, ShieldI2CBase
#from digitalio import DigitalInOut, Direction
#from analogio import AnalogIn
#import microcontroller

#from LumensalisCP.CPTyping import Any, Callable, Generator, List, Mapping, Tuple


class D1MiniPinProxy(PinProxy):
    pass
  
    
class D1MiniBoardBase(ShieldI2CBase):
    def __init__(self, **kwds ):
        super().__init__( **kwds )
        
        print( f"D1MiniBoardBase.__init__( {kwds})")
        assert self.main is not None
        
        self.TX = D1MiniPinProxy( 'TX', self )
        self.RX = D1MiniPinProxy( 'RX', self )
        self.SDA= D1MiniPinProxy( 'SDA', self )
        self.SCL= D1MiniPinProxy( 'SCL', self )
        self.D0= D1MiniPinProxy( 'D0', self )
        self.D1= D1MiniPinProxy( 'D1', self )
        self.D2= D1MiniPinProxy( 'D2', self )
        self.D3= D1MiniPinProxy( 'D3', self )
        self.D4= D1MiniPinProxy( 'D4', self )
        self.D5= D1MiniPinProxy( 'D5', self )
        self.D6= D1MiniPinProxy( 'D6', self )
        self.D7= D1MiniPinProxy( 'D7', self )
        self.D8= D1MiniPinProxy( 'D8', self )
        self.A0= D1MiniPinProxy( 'A0', self )
        
        self.main._boards.append(self)
