
import time
import LumensalisCP.Controllers.ConfigurableBase
import board
import microcontroller
import busio
import os
import LumensalisCP.Controllers
from LumensalisCP.Controllers.ConfigurableBase import ConfigurableBase

class BoardBase(ConfigurableBase):
    def __init__(self, config=None, **kwds ):
        super().__init__( config, **kwds )

    def dbgOut(self, fmt, *args, **kwds): 
        print( fmt.format(*args,**kwds) )

    def initI2C(self): 
        i2c = self.config.option('i2c')
        sdaPin = self.config.SDA
        sclPin = self.config.SCL
        
        if i2c is None:
            if sdaPin is None and sclPin is None:
                i2c = board.I2C()
            else:
                self.dbgOut( "initializing busio.I2C, scl={}, sda={}", sclPin, sdaPin )
                i2c =  busio.I2C( sdaPin, sclPin ) 

        assert( i2c is not None )
        
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

