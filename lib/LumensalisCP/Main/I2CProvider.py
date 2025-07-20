
from LumensalisCP.Identity.Local import NamedLocalIdentifiableList
from LumensalisCP.common import *
from LumensalisCP.commonCP import *
from LumensalisCP.CPTyping import *

import busio
import board
from LumensalisCP.I2C.I2CDevice import I2CDevice
if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    from LumensalisCP.Debug import Debuggable

class I2CProvider(Debuggable):
    def __init__(self,config, main:MainManager):
        
        
        self._i2cDevicesContainer = NamedLocalIdentifiableList(name='i2cDevices',parent=main)
        
        self.infoOut( "I2CProvider init %r, %r", config, main )
        import LumensalisCP.I2C.I2CFactory
        import LumensalisCP.I2C.Adafruit.AdafruitI2CFactory
        self.adafruitFactory =  LumensalisCP.I2C.Adafruit.AdafruitI2CFactory.AdafruitFactory(main=main)
        self.i2cFactory =  LumensalisCP.I2C.I2CFactory.I2CFactory(main=main)
        self.__i2cChannels:dict[tuple[int|str,int|str],busio.I2C] = {}

        self.__i2cDevices:List[I2CDevice] = []
        self.__defaultI2C:busio.I2C|None = None
        self.__identityI2C = None
        i2c = config.option('i2c')
        sdaPin = config.SDA
        sclPin = config.SCL
        
        if i2c is None and self is main:
            if sdaPin is not None and sclPin is not None:
                self.infoOut( "initializing busio.I2C, scl=%s, sda=%s", sclPin, sdaPin )
                try:
                    i2c =  self.addI2C( self.asPin(sdaPin), self.asPin(sclPin) ) 
        #
        #            if ENABLE_EEPROM_IDENTITY:
        #                eeprom = adafruit_24lc32.EEPROM_I2C(i2c_bus=i2c, max_size=1024)
        #                self.__identityI2C = ControllerNVM( eeprom )
                except Exception as inst:
                    SHOW_EXCEPTION( inst, f"I2C identity exception ")


    def asPin(self, pin ) -> microcontroller.Pin: ...
    
    @property
    def defaultI2C(self): return self.__defaultI2C or board.I2C()
            
    def _addI2CDevice(self, target:I2CDevice ):
        self.__i2cDevices.append(target)
        target.nliSetContainer(self._i2cDevicesContainer)
   
    def _addBoardI2C( self, board, i2c:busio.I2C ):
        if self.__defaultI2C is None:
            self.__defaultI2C = i2c

    @property
    def identityI2C(self): return self.__identityI2C

    def addI2C(self, sdaPin, sclPin):
        sdaPin = self.asPin(sdaPin)
        sclPin = self.asPin(sclPin)
        sdaPinName = repr(sdaPin)
        sclPinName = repr(sclPin)
        self.infoOut( "addI2C( %r, %r ) %r", sdaPin, sclPin, self.__i2cChannels )
        for pins, channel in self.__i2cChannels.items():
            if pins[0] != sdaPinName and pins[1] != sclPinName:
                continue
            ensure( pins[0] == sdaPinName , "sda mismatch" )
            ensure( pins[1] == sclPinName , "scl mismatch" )
            return channel
        
        i2c =  busio.I2C( sdaPin, sclPin ) 
        self.__i2cChannels[ (sdaPinName,sclPinName) ] = i2c
        self._addBoardI2C( self, i2c )
        return i2c
