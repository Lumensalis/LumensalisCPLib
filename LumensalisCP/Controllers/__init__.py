import microcontroller, neopixel, board


# Map from specific controllers actual pins to D1 Mini pin names
class ControllerPins(object):
    
    pinNames = [ "D0","D1","D2","D3","D4","D5","D6","D7","D8","A0","TX","RX" ]
    
    def __init__(self, **kwds):
        

        for pinName in ControllerPins.pinNames:
            pinTag = kwds.get( pinName, pinName )
            pin = self.lookupPin( pinTag )
            setattr(self, pinName, pin )
    
    def lookupPin( self, tag:str ):
        if tag.startswith("m"):
            pin = getattr( microcontroller.pin, tag[1:] )
        elif tag.startswith("b"):
            pin = getattr(board, tag[1:] )
        #elif tag.startswith("D"):
        #    pin = getattr(board, tag[1:] )
        elif tag.startswith("GPIO"):
            pin = getattr( microcontroller.pin, tag )
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
        self.options[tag] = val
        setattr( self, tag, val )
        
    def option( self, tag, default=None ):
        if tag in ControllerPins.pinNames:
            return getattr( self.pins, tag )
        return self.options.get( tag, default )
    
    def updateDefaultOptions( self, **kwds ):
        for tag,val in kwds.items():
            if tag not in self.options:
                self.setOption( tag, val)

configs = {
    'lolin_s2_mini' : ControllerConfig(
        TX = "GPIO39",
        RX = "GPIO37",
        D1 = "GPIO35", #SCL
        D2 = "GPIO33", #SDA
        D3 = "GPIO18",
        D4 = "GPIO16",
        
        A0 = "GPIO3",
        D0 = "GPIO5",
        D5 = "GPIO7",
        D6 = "GPIO9",
        D7 = "GPIO11",
        D8 = "GPIO12",
     ),
    
     'lolin_s2_mini_b' : ControllerConfig(
        TX = "GPIO40",
        RX = "GPIO38",
        D1 = "GPIO36", #SCL
        D2 = "GPIO34", #SDA
        D3 = "GPIO21",
        D4 = "GPIO17",
        
        A0 = "GPIO2",
        D0 = "GPIO4",
        D5 = "GPIO6",
        D6 = "GPIO8",
        D7 = "GPIO10",
        D8 = "GPIO13",
     ),
    'lilygo_ttgo_t-oi-plus' :  ControllerConfig(
        TX = "GPIO21",
        RX = "GPIO20",
        D1 = "GPIO19", #SCL
        D2 = "GPIO18", #SDA
        D3 = "GPIO9",
        D4 = "GPIO8",
        
        A0 = "GPIO2",
        D0 = "GPIO4",
        D5 = "GPIO5",
        D6 = "GPIO6",
        D7 = "GPIO7",
        D8 = "GPIO10",
     )
        
    
}