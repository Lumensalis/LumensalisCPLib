from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.IOContext import InputSource, OutputTarget, UpdateContext, NamedLocalIdentifiable

import busio
#import weakref

class I2CDeviceInitArgs(TypedDict):
    i2c: busio.I2C
    main: "LumensalisCP.Main.Manager.MainManager"
    address: int
    updateInterval:float|None

class I2CDevice( NamedLocalIdentifiable ):
    def __init__(self, i2c=None, main:"LumensalisCP.Main.Manager.MainManager"=None,
                 address:int|None = None, updateInterval:float|None = None,
                 name:str=None
        ):
        super().__init__(name=name or self.__class__.__name__)
        
        assert main is not None

        self.__i2c = i2c or main.defaultI2C
        self.__main = main
        self.__latestUpdateIndex:int = -1
        self.__address = address
        self.__updates = 0
        self.__updateInterval = updateInterval
        self.__nextUpdate:float = updateInterval
        main._addI2CDevice(self)
    

        
    @property
    def i2c(self): return self.__i2c
    
    @property
    def main(self): return self.__main
    
    def derivedUpdateTarget(self, context:UpdateContext):
        raise NotImplemented
    
    def updateTarget(self, context:UpdateContext) -> bool:
        if not self.__updateInterval: return False
        now = context.when or self.__main.when
        if self.__nextUpdate is not None and self.__nextUpdate > now:
            return False
        
        if self.__latestUpdateIndex == context.updateIndex:
            return False
        with context.subFrame('updateTarget',self.name) as frame:
            self.__updates += 1
            self.__latestUpdateIndex = context.updateIndex
            self.__nextUpdate = now + self.__updateInterval
            frame.snap("callDerived")
            self.derivedUpdateTarget( context )
        return True
        
        
class I2CInputSource( InputSource ):
    def __init__(self, target:I2CDevice = None, **kwargs ):
        super().__init__(**kwargs)
        self._wrTarget = target # weakref.ref(target)

    @property
    def parentTarget(self): return self._wrTarget
    
    
class I2COutputTarget( OutputTarget ):
    def __init__(self, target:I2CDevice = None, **kwargs ):
        super().__init__(**kwargs)
        self._wrTarget = target # weakref.ref(target)

    @property
    def parentTarget(self): return self._wrTarget    