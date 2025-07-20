from __future__ import annotations
from LumensalisCP.commonCP import *

#from LumensalisCP.IOContext import *
from LumensalisCP.Eval.common import *
from LumensalisCP.Identity.Local import NamedLocalIdentifiableContainerMixin, NamedLocalIdentifiableList, NamedLocalIdentifiable

if TYPE_CHECKING:
    import LumensalisCP.Main.Manager
    from  LumensalisCP.Main.Manager import MainManager

#############################################################################

class I2CDeviceInitArgs(TypedDict):
    i2c: busio.I2C
    main: MainManager
    address: int
    updateInterval:float|None

class I2CDevice( NamedLocalIdentifiable ):
    def __init__(self, main:MainManager, i2c=None, 
                 address:int|None = None, updateInterval:float|None = None,
                 name:Optional[str]=None
        ):
        super().__init__(name=name or self.__class__.__name__)
        
        assert main is not None

        self.__i2c = i2c or main.defaultI2C
        self.__main = main
        self.__latestUpdateIndex:int = -1
        self.__address = address
        self.__updates = 0  
        self.__updateInterval = updateInterval
        self.__nextUpdate:float = main.when
        main._addI2CDevice(self)
    
        self._inputs = NamedLocalIdentifiableList(name='inputs',parent=self)
        self._outputs = NamedLocalIdentifiableList(name='outputs',parent=self)
        

    def nliGetContainers(self) -> Iterable[NamedLocalIdentifiableContainerMixin]|None:
        yield self._inputs
        yield self._outputs
        
            
    @property
    def i2c(self): return self.__i2c
    
    @property
    def main(self): return self.__main

    @property
    def address(self) -> int|None: return self.__address
    
    @property
    def updates(self) -> int: return self.__updates
    
    
    def derivedUpdateTarget(self, context:EvaluationContext) -> None:
        raise NotImplementedError( 'derivedUpdateTarget' )

    def updateTarget(self, context:EvaluationContext) -> bool:
        if not self.__updateInterval: return False
        now = context.when or self.__main.when
        if self.__nextUpdate is not None and self.__nextUpdate > now:
            return False
        
        if self.__latestUpdateIndex == context.updateIndex:
            return False
        with context.subFrame('updateTarget',self.name) as frame:
            self.__updates += 1  # pylint: disable=unused-private-member
            self.__latestUpdateIndex = context.updateIndex
            self.__nextUpdate = now + self.__updateInterval
            frame.snap("callDerived")
            self.derivedUpdateTarget( context )
        return True
        
        
class I2CInputSource( InputSource ):
    def __init__(self, target:I2CDevice, **kwargs ):
        super().__init__(**kwargs)
        self._wrTarget = target # weakref.ref(target)
        self.nliSetContainer(target._inputs)

    @property
    def parentTarget(self): return self._wrTarget
    
    
class I2COutputTarget( NamedOutputTarget ): # pylint: disable=abstract-method
    def __init__(self, target:I2CDevice, **kwargs ):
        super().__init__(**kwargs)
        self._wrTarget = target # weakref.ref(target)
        self.nliSetContainer(target._outputs)
    @property
    def parentTarget(self): return self._wrTarget    
