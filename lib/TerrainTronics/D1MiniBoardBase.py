

from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__profileImport = getImportProfiler( __name__, globals() )

#############################################################################

from LumensalisCP.CPTyping import Unpack
from LumensalisCP.Shields.Pins import PinProxy
from LumensalisCP.Shields.Base import ShieldI2CBase

#############################################################################
__profileImport.parsing()

class D1MiniPinProxy(PinProxy):
    pass
  
class D1MiniBoardBase(ShieldI2CBase): # pylint: disable=abstract-method


    def __init__(self, **kwds:Unpack[ShieldI2CBase.KWDS] ):
        super().__init__( **kwds )
        
        #print( f"D1MiniBoardBase.__init__( {kwds})")
        
        main = getattr(self,'main',None)
        assert main is not None
        
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
        
        
#############################################################################
__profileImport.complete()
