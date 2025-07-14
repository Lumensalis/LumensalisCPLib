
thisModuleIsIShieldsBase = True
#import busio
from LumensalisCP.Controllers.ConfigurableBase import ControllerConfigurableChildBase
#from LumensalisCP.Inputs import InputSource
from LumensalisCP.IOContext import NamedOutputTarget, EvaluationContext, Refreshable

#from LumensalisCP.Shields.Pins import PinHolder, PinProxy
#from digitalio import DigitalInOut, Direction
from LumensalisCP.Main.I2CProvider import I2CProvider


class ShieldBase(ControllerConfigurableChildBase,Refreshable):
    def __init__(self, refreshRate=0.1, **kwds ):
        super().__init__( **kwds )
        Refreshable.__init__(self,refreshRate=refreshRate)
        

    def mcPostCreate(self): 
        super().mcPostCreate()
        self.nliContainer =  self.main.shields
        

class ShieldI2CBase(ShieldBase,I2CProvider):
    def __init__(self, refreshRate=0.1, config=None, main=None, **kwds ):
        ShieldBase.__init__( self, refreshRate=refreshRate, config=config, main=main,**kwds )
        
        I2CProvider.__init__( self, config=self.config, main=main )

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
            assert( i2c is not None )        
            
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

        