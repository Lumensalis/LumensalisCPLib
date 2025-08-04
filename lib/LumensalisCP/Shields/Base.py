
from LumensalisCP.ImportProfiler import getImportProfiler
__sayImport = getImportProfiler( globals() )

from LumensalisCP.IOContext import *

from LumensalisCP.Controllers.ConfigurableBase import ControllerConfigurableChildBase

from LumensalisCP.Inputs import NamedLocalIdentifiable
from LumensalisCP.Main.I2CProvider import I2CProvider


class ShieldBase(ControllerConfigurableChildBase):#,RfMxnActivatablePeriodic, Refreshable): # pylint: disable=abstract-method
    class KWDS(ControllerConfigurableChildBase.KWDS):#,RfMxnActivatablePeriodic.KWDS, Refreshable.KWDS):
        pass
        
    def __init__(self, **kwds:Unpack[KWDS] ) -> None:
        main = kwds.get('main')
        #assert main is not None, "ShieldBase must be created with a main instance"
        #kwds.setdefault('autoList',main.refreshables)
        #Refreshable.__init__(self, mixinKwds=kwds )
        ControllerConfigurableChildBase.__init__(self, **kwds )
        #assert self.main is not None, "ShieldBase must be created with a main instance"
        
        self.__componentsContainer:NliList[NamedLocalIdentifiable] = NliList("components", parent=self)
        self.activate(main.getContext())

    def nliGetContainers(self) -> Iterable[NliContainerMixin[NamedLocalIdentifiable]]:
        return [ self.__componentsContainer ]
    
    def nliAddComponent(self, component:NamedLocalIdentifiable):
        component.nliSetContainer(self.__componentsContainer)
    
    def mcPostCreate(self): 
        super().mcPostCreate()
        self.nliSetContainer( self.main.shields )
        

class ShieldI2CBase(ShieldBase,I2CProvider):  # pylint: disable=abstract-method
    # pylint: disable=attribute-defined-outside-init
    
        
    def __init__(self, **kwds:Unpack[ShieldBase.KWDS] ):
        ShieldBase.__init__( self, **kwds )
        
        I2CProvider.__init__( self, config=self.config, main=self.main )

    def initI2C(self): 
        i2c = self.config.option('i2c')
        sdaPin = self.config.SDA
        sclPin = self.config.SCL    
        
        if i2c is None :
            if sdaPin is None and sclPin is None:
                i2c = self.main.defaultI2C
            else:
                self.infoOut( "initializing busio.I2C, scl=%s, sda=%s", sclPin, sdaPin )
                i2c =  self.main.addI2C( sdaPin, sclPin ) 
            assert i2c is not None
            
        if i2c is not None:

            self.i2c = i2c
            self.sdaPin = sdaPin
            self.sclPin = sclPin
        
    def scanI2C(self):
        print( "scanning i2c\n")
                
        while not self.i2c.try_lock():
            pass

        try:
            #while True:
            print(
                "I2C addresses found:",
                [hex(device_address) for device_address in self.i2c.scan()],
                )
            #   time.sleep(2)

        finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
            self.i2c.unlock()

        print( "i2c scan complete\n")


__all__ = [
    'ShieldBase',
    'ShieldI2CBase',
]

__sayImport.complete()
