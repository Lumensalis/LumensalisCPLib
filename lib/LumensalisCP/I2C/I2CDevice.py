from __future__ import annotations

from LumensalisCP.Main.PreMainConfig import ImportProfiler
_sayI2CDeviceImport = ImportProfiler( "I2C.I2CDevice" )


from LumensalisCP.commonCP import *
from LumensalisCP.IOContext import *


#############################################################################


class I2CDevice( NamedLocalIdentifiable ):
    """Base class for I2C devices."""
    
    DEFAULT_UPDATE_INTERVAL:ClassVar[TimeInSeconds] = TimeInSeconds(0.1)

    class KWDS(NamedLocalIdentifiable.KWDS):
        #main: Required[MainManager]
        i2c: NotRequired[busio.I2C]
        address: NotRequired[int]
        updateInterval:NotRequired[TimeInSecondsConfigArg]
    
    def __init__(self:'I2CDevice', main:MainManager, i2c:Optional[busio.I2C]=None, 
                 address:int|None = None, updateInterval:Optional[TimeInSecondsConfigArg] = None,
                 **kwds:Unpack[NamedLocalIdentifiable.KWDS]
        ):
        super().__init__(**kwds)
        assert main is not None

        self.__i2c:busio.I2C = i2c or main.defaultI2C
        self.__main = main
        self.__latestUpdateIndex:int = -1
        self.__address = address
        self.__updates = 0  
        self.__derivedUpdateChanges = 0
        self.__nextUpdate:TimeInSeconds|None = None 
        if updateInterval is not None:  
            self.__updateInterval:TimeInSeconds = TimeInSeconds(updateInterval)
        else:
            self.__updateInterval = self.DEFAULT_UPDATE_INTERVAL 
            
        main._addI2CDevice(self)
    
        self._inputs:NliList[InputSource] = NliList(name='inputs',parent=self)
        self._outputs:NliList[NamedOutputTarget] = NliList(name='outputs',parent=self)
        

    def nliGetContainers(self)->Iterable[NliContainerBaseMixin]|None:
        assert isinstance(self._inputs, NliContainerBaseMixin), "inputs must be a NliContainerBaseMixin"
        yield self._inputs
        assert isinstance(self._outputs, NliContainerBaseMixin), "outputs must be a NliContainerBaseMixin"
        yield self._outputs
        
            
    @property
    def i2c(self): return self.__i2c
    
    @property
    def main(self): return self.__main

    @property
    def address(self) -> int|None: return self.__address
    
    @property
    def updates(self) -> int: return self.__updates
    
    @property
    def changes(self) -> int: return self.__derivedUpdateChanges
    

    def derivedUpdateDevice(self, context:EvaluationContext) -> bool|None:
        """Override this method to implement the device update logic.
        Return True if changes were detected
        """
        raise NotImplementedError( 'derivedUpdateDevice' )

    def _markChanged(self, context:EvaluationContext) -> None: # pylint: disable=unused-argument
        self.__derivedUpdateChanges += 1
        
    def updateDevice(self, context:EvaluationContext) -> bool:
        if not self.__updateInterval: return False
        now = context.when or self.__main.when
        if self.__nextUpdate is not None and self.__nextUpdate > now:
            return False
        
        if self.__latestUpdateIndex == context.updateIndex:
            return False
        with context.subFrame('updateDevice',self.name) as frame:
            self.__updates += 1  # pylint: disable=unused-private-member
            self.__latestUpdateIndex = context.updateIndex
            self.__nextUpdate = now + self.__updateInterval # type: ignore
            frame.snap("callDerived")
            if self.derivedUpdateDevice( context ):
                self._markChanged(context)
        return True
        
        
class I2CInputSource( InputSource ): # pylint: disable=abstract-method
    
    class KWDS(InputSource.KWDS):
        pass

    def __init__(self, target:I2CDevice,  **kwds:Unpack[InputSource.KWDS] ):
        super().__init__(**kwds)
        self._wrTarget = target # weakref.ref(target)
        self.nliSetContainer(target._inputs) # type: ignore

    @property
    def parentTarget(self): return self._wrTarget

class I2COutputTarget( NamedOutputTarget ): # pylint: disable=abstract-method
    def __init__(self, target:I2CDevice, **kwargs:Unpack[NamedOutputTarget.KWDS] ):
        super().__init__(**kwargs)
        self._wrTarget = target # weakref.ref(target)
        self.nliSetContainer(target._outputs) # type: ignore
    @property
    def parentTarget(self): return self._wrTarget    

_sayI2CDeviceImport.complete()
