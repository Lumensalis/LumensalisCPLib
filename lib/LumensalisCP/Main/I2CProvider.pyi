from __future__ import annotations

import busio
import board

from LumensalisCP.Identity.Local import NliList
from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
from LumensalisCP.I2C.I2CDevice import I2CDevice
import LumensalisCP.I2C.I2CFactory
import LumensalisCP.I2C.Adafruit.AdafruitI2CFactory

# pylint: disable=unused-argument,redefined-outer-name
class I2CProvider(object):
    def __init__(self,config = None, main=None): pass
        
        
    i2cDevicesContainer: NliList[I2CDevice]
    adafruitFactory : LumensalisCP.I2C.Adafruit.AdafruitI2CFactory.AdafruitFactory
    i2cFactory: LumensalisCP.I2C.I2CFactory.I2CFactory
    __i2cChannels:Mapping[Tuple[int,int],busio.I2C]
    __i2cDevices:List[I2CDevice]
    __defaultI2C:busio.I2C
    __identityI2C:Any


    defaultI2C:busio.I2C
            
    def _addI2CDevice(self, target:I2CDevice ): ...
    
    def _addBoardI2C( self, board, i2c:busio.I2C ): ...
    
    @property
    def identityI2C(self): return self.__identityI2C

    def addI2C(self, sdaPin, sclPin) -> busio.I2C: ...
