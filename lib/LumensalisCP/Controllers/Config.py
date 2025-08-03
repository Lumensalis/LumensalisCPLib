from __future__ import annotations
import microcontroller, board # type: ignore # pylint: disable=all


from LumensalisCP.common import Any, Optional, TypeAlias, Union, StrAnyDict, CountedInstance
# Map from specific controllers actual pins to D1 Mini pin names
class ControllerPins(CountedInstance):
    
    pinNames = [ "D0","D1","D2","D3","D4","D5","D6","D7","D8","A0","TX","RX" ]
    
    def __init__(self, **kwds:dict[str,Any]): 
        super().__init__()

        for pinName in ControllerPins.pinNames:
            pinTag = kwds.get( pinName, pinName ) 
            if isinstance(pinTag,str):
                pin = self.lookupPin( pinTag )
            else: pin = pinTag
            assert isinstance(pin, microcontroller.Pin)
            setattr(self, pinName, pin )
    
    def lookupPin( self, tag:str ) -> microcontroller.Pin :
        if tag.startswith("m"):
            pin = getattr( microcontroller.pin, tag[1:] ) # type: ignore
        elif tag.startswith("b"):
            pin = getattr(board, tag[1:] )
        #elif tag.startswith("D"):
        #    pin = getattr(board, tag[1:] )
        elif tag.startswith("GPIO"):
            pin = getattr( microcontroller.pin, tag ) # type: ignore
        else:
            pin = getattr(board, tag, None )
        assert pin is not None 
        return pin
            
    def __getattr__(self, tag:str)-> microcontroller.Pin:
        raise AttributeError(f"ControllerPins has no pin {tag!r}")
    
class ControllerConfig(CountedInstance):
    
    options:dict[str,Any]
    
    def __init__( self, **kwds:Any ) -> None:
        super().__init__()
        self.kwds = dict(**kwds)
        self.pins = None
        # self.options = None
    
    TX = property( lambda self: self.pins.TX )
    RX = property( lambda self: self.pins.RX )
    SDA = property( lambda self: self.pins.D1 )
    SCL = property( lambda self: self.pins.D2 )
    D1 = property( lambda self: self.pins.D1 )
    D2 = property( lambda self: self.pins.D2 )
    D3 = property( lambda self: self.pins.D3 )
    D4 = property( lambda self: self.pins.D4 )
    D5 = property( lambda self: self.pins.D5 )
    D6 = property( lambda self: self.pins.D6 )
    D7 = property( lambda self: self.pins.D7 )
    D8 = property( lambda self: self.pins.D8 )
    A0 = property( lambda self: self.pins.A0 )
    
    def copy(self):
        
        assert self.pins is None 
        assert getattr(self,'options',None) is None 
        return ControllerConfig( **self.kwds )

    def bake( self, **kwds:dict[str,Any] ):
        self.kwds.update( kwds )
        self.pins = ControllerPins(**self.kwds )
        self.options = {}
        
        for tag,val in kwds.items():
            if tag not in ControllerPins.pinNames:
                self.setOption( tag, val )
    
    def setOption( self, tag:str, val:Any ):
        assert self.options is not None
        self.options[tag] = val
        setattr( self, tag, val )

    def  getRequiredPin( self, tag:str, default:Optional[microcontroller.Pin]=None ) -> microcontroller.Pin :
        if tag in ControllerPins.pinNames:
            rv = getattr( self.pins, tag )
        else:
            assert self.options is not None
            rv =  self.options.get( tag, default )
        assert isinstance(rv, microcontroller.Pin)
        return rv
            
    def option( self, tag:str, default:Any=None ):
        if tag in ControllerPins.pinNames:
            return getattr( self.pins, tag )
        assert self.options is not None
        return self.options.get( tag, default )
    
    def updateDefaultOptions( self, **kwds:dict[str,Any] ):
        assert self.options is not None
        for tag,val in kwds.items():
            if tag not in self.options:
                self.setOption( tag, val)

ControllerConfigArg: TypeAlias = Union[ControllerConfig , str , StrAnyDict ]