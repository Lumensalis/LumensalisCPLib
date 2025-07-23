
from LumensalisCP.IOContext import *

from LumensalisCP.Controllers.ConfigurableBase import ControllerConfigurableChildBase
#from LumensalisCP.Inputs import InputSource
from LumensalisCP.Main.Refreshable import Refreshable

#from LumensalisCP.Shields.Pins import PinHolder, PinProxy
#from digitalio import DigitalInOut, Direction
from LumensalisCP.Identity.Local import NliList, NliContainerMixin
from LumensalisCP.Inputs import NamedLocalIdentifiable
from LumensalisCP.Main.I2CProvider import I2CProvider


class ShieldBase(ControllerConfigurableChildBase,Refreshable): # pylint: disable=abstract-method
    class KWDS(ControllerConfigurableChildBase.KWDS):
        refreshRate: NotRequired[float] 
        
    def __init__(self, refreshRate=0.1, **kwds:Unpack[ControllerConfigurableChildBase.KWDS] ):
        ControllerConfigurableChildBase.__init__(self, **kwds )
        Refreshable.__init__(self,refreshRate=refreshRate) # type: ignore
        self.__componentsContainer:NliList = NliList("components", parent=self)
        
    def nliGetContainers(self) -> Iterable[NliContainerMixin]:
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
