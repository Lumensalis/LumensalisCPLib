class ControlVariable(object):
    def __init__(self, name:str, description:str="", kind:str=None, startingValue=None,
                 min = None, max = None ):
        self.name = name
        self.description = description or name
        self.kind = kind
        
        self._min = min
        self._max = max
        
        self._value = startingValue or min or max

    value = property( lambda self: self._value )
    
    def setFromWs( self, value ):
        if self.kind == 'RGB':
            if type(value) == str:
                try:
                    rgb = ( int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16) )
                    value = rgb
                    # print( f"rgb converted {value} to {rgb}" )
                except Exception as inst:
                    print( f"failed converting {value} to RGB" )
                
        self.set( value )
        
    def set( self, value ):
        if value != self._value:
            if self._min is not None and value < self._min:
                value = self._min
            elif self._max is not None and value > self._max:
                value = self._max
            
            if value != self._value:
                self._value = value
    
    def move( self, delta ):
        self.set( self._value + delta )
