import microcontroller, board

# Map from specific controllers actual pins to D1 Mini pin names
class ControllerPins(object):
    
    pinNames = [ "D0","D1","D2","D3","D4","D5","D6","D7","D8","A0","TX","RX" ]
    
    def __init__(self, **kwds):
        

        for pinName in ControllerPins.pinNames:
            pinTag = kwds.get( pinName, pinName )
            pin = self.lookupPin( pinTag )
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
        assert( pin is not None )
        return pin
            
class ControllerConfig(object):
    def __init__( self, **kwds ):
        self.kwds = dict(**kwds)
        self.pins = None
        self.options = None
    
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
        
        assert( self.pins is None )
        assert( self.options is None )
        return ControllerConfig( **self.kwds )
        
    def bake( self, **kwds ):
        self.kwds.update( kwds )
        self.pins = ControllerPins(**self.kwds )
        self.options = {}
        
        for tag,val in kwds.items():
            if tag not in ControllerPins.pinNames:
                self.setOption( tag, val )
    
    def setOption( self, tag, val ):
        assert self.options is not None
        self.options[tag] = val
        setattr( self, tag, val )
        
    def option( self, tag, default=None ):
        if tag in ControllerPins.pinNames:
            return getattr( self.pins, tag )
        assert self.options is not None
        return self.options.get( tag, default )
    
    def updateDefaultOptions( self, **kwds ):
        assert self.options is not None
        for tag,val in kwds.items():
            if tag not in self.options:
                self.setOption( tag, val)
