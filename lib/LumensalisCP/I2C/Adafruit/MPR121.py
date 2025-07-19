
from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from ..I2CDevice import I2CDevice, I2CInputSource, UpdateContext

import adafruit_mpr121

class MPR121Input(I2CInputSource):
    def __init__( self, pin:int = None, **kwargs ):
        super().__init__(**kwargs)
        self.__pin = pin
        self.__mask = 1 << pin
        self._touched:bool = False

    @property 
    def pin(self): return self.__pin
    
    def getDerivedValue(self, context:EvaluationContext) -> bool:
        return self._touched
    
    def _setTouched( self, allTouched, context:EvaluationContext):
        touched = (allTouched & self.__mask) != 0
        if self._touched != touched:
            self._touched = touched
            if self.enableDbgOut: self.dbgOut( "MPR121Input = %s", touched )
            self.updateValue( context )
            

class MPR121(I2CDevice,adafruit_mpr121.MPR121):
    MPR121_PINS = 11
    
    def __init__(self, *args, **kwds ):
        updateKWDefaults( kwds,
            updateInterval = 0.1,
        )
        
        I2CDevice.__init__( self, *args,**kwds )
        adafruit_mpr121.MPR121.__init__(self, self.i2c)
        self.__lastTouched:int = 0
        self.__inputs:List[MPR121Input|None] = [None] * MPR121.MPR121_PINS
        
        self.__unusedPinsMask = 0
        self.__usedPinsMask = 0
        self.__updateUnusedPinMask()

        self.__onUnusedCB = None
        self.__latestUnused = 0

        self.__updates = 0
        self.__changes = 0

    @property
    def inputs(self): return list(filter( lambda i: i is not None, self.__inputs ))
    
    @property
    def lastTouched(self): return self.__lastTouched
        
    def addInput( self, pin:Optional[int]=None, name:str = None ):
        assert pin >= 0 and pin < len(self.__inputs)
        input = self.__inputs[pin]
    
        if input is not None:
            ensure( name == input.name, "%r != %r", name, input.name )
        else:
            input = MPR121Input( pin=pin, name=name, target=self)
            self.__inputs[pin] = input
            self.__updateUnusedPinMask()
        return input

    def addInputs( self, *inArgs ) -> list[MPR121Input]:
        rv = []
        for inArg in inArgs:
            if isinstance( inArg, (tuple,list) ):
                pin, name = inArg
            else:
                pin,name = inArg, None
            rv.append( self.addInput(pin,name) )
        return rv
        
    
    @property 
    def touchedInputs( self ):
        return filter( lambda input: input is not None and input, self.__inputs )

    @property 
    def touchedPins( self ):
        activePins = []
        touched = self.lastTouched
        for pin in range( self.MPR121_PINS ):
            if touched & (1 << pin):
                activePins.append(pin)
        return activePins

    
    def onUnused( self, cb:Callable):
        self.__onUnusedCB = cb
                    
    def derivedUpdateTarget(self, context:EvaluationContext):
        with context.stubFrame('dUpdateTarget', self.name) as frame:
            frame.snap( "getTouched")
            allTouched = self.touched()
            frame.snap( "updateInternal")
            self.__updates += 1
            if self.__lastTouched != allTouched:
                used =  allTouched & self.__usedPinsMask
                priorUsed = self.__lastTouched & self.__usedPinsMask
                
                self.__lastTouched = allTouched
                self.__changes += 1
                
                if used != priorUsed:
                    frame.snap( "updateInputs")
                    for input in self.__inputs:
                        if input is not None:
                            input._setTouched( allTouched, context )                    
                    
                unused = allTouched & self.__unusedPinsMask
                #self.dbgOut( "MPR121 = %X, unused=%X, upm=%X",  allTouched, unused, self.__unusedPinsMask )
                
                if unused != self.__latestUnused:
                    self.__latestUnused = unused
                    if self.__onUnusedCB is not None:
                        #self.dbgOut( "calling unusedCB( %r, %r)", unused, context )
                        self.__onUnusedCB( unused = unused, context = context )
                

        

            
    def __updateUnusedPinMask(self):
            unusedPinsMask = 0
            usedPinsMask = 0
            for pin in range(MPR121.MPR121_PINS):
                if self.__inputs[pin] is None:
                    unusedPinsMask |= ( 1 << pin )
                else:
                    usedPinsMask |= ( 1 << pin )
            self.__unusedPinsMask = unusedPinsMask
            self.__usedPinsMask = usedPinsMask
            
