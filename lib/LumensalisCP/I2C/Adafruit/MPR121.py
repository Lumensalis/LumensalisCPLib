from __future__ import annotations

import adafruit_mpr121
from LumensalisCP.I2C.common import *

class MPR121Input(I2CInputSource):
    def __init__( self, target:MPR121, pin:int, **kwargs:Unpack[I2CInputSource.KWDS] ):
        super().__init__( target, **kwargs)
        self.__pin = pin
        self.__mask = 1 << pin
        self._touched:bool = False

    @property 
    def pin(self): return self.__pin
    
    def getDerivedValue(self, context:EvaluationContext) -> bool: # pylint: disable=unused-argument
        return self._touched
    
    def _setTouched( self, allTouched:int, context:EvaluationContext):
        touched = (allTouched & self.__mask) != 0
        if self._touched != touched:
            self._touched = touched
            if self.enableDbgOut: self.dbgOut( "MPR121Input = %s", touched )
            self.updateValue( context )

MPR121UnusedInputCallbackType:TypeAlias = Callable[[int, EvaluationContext], None]
class MPR121(I2CDevice,adafruit_mpr121.MPR121):
    DEFAULT_UPDATE_INTERVAL = TimeInSeconds(0.1)  # type: ignore
    MPR121_PINS = 11
    
    def __init__(self, main:MainManager, **kwds:Unpack[I2CDevice.KWDS] ):
        
        I2CDevice.__init__( self, main=main, **kwds )
        adafruit_mpr121.MPR121.__init__(self, self.i2c) # type: ignore
        self.__lastTouched:int = 0
        self.__inputs:List[MPR121Input|None] = [None] * MPR121.MPR121_PINS
        
        self.__unusedPinsMask = 0
        self.__usedPinsMask = 0
        self.__updateUnusedPinMask()

        self.__onUnusedCB = None
        self.__latestUnused = 0

    @property
    def inputs(self): return list(filter( lambda i: i is not None, self.__inputs ))
    
    @property
    def lastTouched(self): return self.__lastTouched
        
    def addInput( self, pin:int, **kwds:Unpack[MPR121Input.KWDS] ) -> MPR121Input:
        assert pin >= 0 and pin < len(self.__inputs)
        inputSource = self.__inputs[pin]
    
        if inputSource is not None:
            pass
            #ensure( name == inputSource.name, "%r != %r", name, inputSource.name )
        else:
            inputSource = MPR121Input( target=self, pin=pin, **kwds)
            self.__inputs[pin] = inputSource
            self.__updateUnusedPinMask()
        return inputSource

    def addInputs( self, *inArgs:Union[tuple[int, Optional[str]], int] ) -> list[MPR121Input]:
        rv:list[MPR121Input] = []
        for inArg in inArgs:
            if isinstance( inArg, (tuple,list) ):
                pin, name = inArg
            else:
                pin,name = inArg, None
            rv.append( self.addInput(pin, name=name) )
        return rv
        
    
    @property 
    def touchedInputs( self ) -> filter[MPR121Input | None]:
        return filter( lambda inputSource: inputSource is not None and inputSource, self.__inputs )

    @property 
    def touchedPins( self ) -> list[int]:
        activePins:list[int] = []
        touched = self.lastTouched
        for pin in range( self.MPR121_PINS ):
            if touched & (1 << pin):
                activePins.append(pin)
        return activePins

    
    def onUnused( self, cb:Callable):
        self.__onUnusedCB = cb
                    
    def derivedUpdateDevice(self, context:EvaluationContext):
        with context.stubFrame('dUpdateDevice', self.name) as frame:
            frame.snap( "getTouched")
            allTouched = self.touched()
            frame.snap( "updateInternal")

            if self.__lastTouched != allTouched:
                used =  allTouched & self.__usedPinsMask
                priorUsed = self.__lastTouched & self.__usedPinsMask
                
                self.__lastTouched = allTouched
                
                if used != priorUsed:
                    frame.snap( "updateInputs")
                    for inputSource in self.__inputs:
                        if inputSource is not None:
                            inputSource._setTouched( allTouched, context ) # pylint: disable=protected-access                    
                    
                unused = allTouched & self.__unusedPinsMask
                #self.dbgOut( "MPR121 = %X, unused=%X, upm=%X",  allTouched, unused, self.__unusedPinsMask )
                
                if unused != self.__latestUnused:
                    self.__latestUnused = unused
                    if self.__onUnusedCB is not None:
                        #self.dbgOut( "calling unusedCB( %r, %r)", unused, context )
                        self.__onUnusedCB( unused = unused, context = context )
                
                return True
                

        

            
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
        
