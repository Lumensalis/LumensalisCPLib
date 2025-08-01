from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
from busio import I2C

_sayI2CDeviceImport = getImportProfiler( globals() ) # "I2C.I2CDevice"

from LumensalisCP.commonCP import *
from LumensalisCP.IOContext import *
from LumensalisCP.Main.Dependents import MainChild

#from LumensalisCP.Temporal.Refreshable import Refreshable, RfMxnActivatablePeriodic
#############################################################################

class I2CDevice( MainChild ):
    """Base class for I2C devices."""
    
    DEFAULT_UPDATE_INTERVAL:ClassVar[TimeSpanInSeconds] = 0.1

    #class KWDS(NamedLocalIdentifiable.KWDS, RfMxnActivatablePeriodic.KWDS, Refreshable.KWDS):
    class KWDS(MainChild.KWDS):
        #main: NotRequired[MainManager]
        i2c: NotRequired[busio.I2C]
        address: NotRequired[int]
    
    def __init__(self, 
                 #main:MainManager,
                 # i2c:Optional[busio.I2C]=None, 
                 #address:int|None = None, 
                 # refreshRate:Optional[TimeInSecondsConfigArg] = None,
                 **kwds:Unpack[KWDS]
            ) -> None:
        #main = kwds.get('main')
        #assert main is not None, "I2CDevice must be created with a main instance"
        i2c = kwds.pop('i2c', None)
        address = kwds.pop('address',None)
        #refreshRate = kwds.get('refreshRate')
        #kwds.setdefault('autoList',main.refreshables)
        #Refreshable.__init__(self, mixinKwds=kwds )
        super().__init__(**kwds)
        assert self.main is not None, "I2CDevice must be created with a main instance"  

        self.__i2c:busio.I2C = i2c or self.main.defaultI2C
        self.__latestUpdateIndex:int = -1
        self.__address = address
        self.__updates = 0  
        self.__derivedUpdateChanges = 0

        self.main.addI2CDevice(self)  # pyright: ignore[reportPrivateUsage]

        self._inputs: NliList[InputSource] = NliList(name='inputs', parent=self)
        self._outputs: NliList[NamedOutputTarget] = NliList(name='outputs', parent=self)

    def nliGetContainers(self)->Iterable[NliContainerBaseMixin]|None:
        assert isinstance(self._inputs, NliContainerBaseMixin), "inputs must be a NliContainerBaseMixin"
        yield self._inputs
        assert isinstance(self._outputs, NliContainerBaseMixin), "outputs must be a NliContainerBaseMixin"
        yield self._outputs
        
            
    @property
    def i2c(self) -> I2C: return self.__i2c
    
    @property
    def main(self) -> MainManager: 
        rv = self.__main()
        assert rv is not None
        return rv

    @property
    def address(self) -> int|None: return self.__address
    
    @property
    def updates(self) -> int: return self.__updates
    
    @property
    def changes(self) -> int: return self.__derivedUpdateChanges
    

    def derivedUpdateDevice(self, context:EvaluationContext) -> bool:
        """Override this method to implement the device update logic.
        Return True if changes were detected
        """
        raise NotImplementedError( 'derivedUpdateDevice' )

    def _markChanged(self, context:EvaluationContext) -> None: # pylint: disable=unused-argument
        self.__derivedUpdateChanges += 1
        
    def derivedRefresh(self, context:EvaluationContext) -> None:
        
        if self.__latestUpdateIndex == context.updateIndex:
            return 
        with context.subFrame('updateDevice',self.name) as frame:
            self.__updates += 1  # pylint: disable=unused-private-member
            self.__latestUpdateIndex = context.updateIndex
            frame.snap("callDerived")
            if self.derivedUpdateDevice( context ):
                self._markChanged(context)

        
#############################################################################

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

#############################################################################

_sayI2CDeviceImport.complete(globals())
