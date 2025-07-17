

import TerrainTronics.D1MiniBoardBase
from LumensalisCP.IOContext import *
from LumensalisCP.commonCP import *
from LumensalisCP.Lights.NeoPixels import NeoPixelSource
from LumensalisCP.Gadgets.IrRemote import LCP_IRrecv, onIRCode
from LumensalisCP.Gadgets.Servos import LocalServo



class CaernarfonCastle(TerrainTronics.D1MiniBoardBase.D1MiniBoardBase):
    
    __servoContainer:NamedLocalIdentifiableList[LocalServo]
    __pixelsContainer:NamedLocalIdentifiableList[NeoPixelSource]
    
    def __init__(self, *args, name=None, **kwds ):
        name = name or "Caernarfon"
        super().__init__( *args, name=name, **kwds )
        c = self.config
        c.updateDefaultOptions( 
                neoPixelPin = c.D3,
                neoPixelCount = 1,
                neoPixelOrder = neopixel.GRB,
                neoPixelBrightness = 0.2,
                servos = 0,
                servo1pin =  c.D6,
                servo2pin =  c.D7,
                servo3pin =  c.D8,
            )
        self._irRemote = None
        self.initI2C()
        self.__pixels:NeoPixelSource = NeoPixelSource(
            c.neoPixelPin, c.neoPixelCount, main = self.main, refreshRate=0.05, brightness=c.neoPixelBrightness, auto_write=False, pixel_order=c.neoPixelOrder
        )
        self.__servoContainer = NamedLocalIdentifiableList("servos", parent=self)
        self.__servos = [ None, None, None ]
        self.__neoPixOnServos = [ None, None, None ]
        self.__pixelsContainer = NamedLocalIdentifiableList("pixels", parent=self)
        self.__allPixels: list[NeoPixelSource] = [self.__pixels]
        
        self.__pixels.nliSetContainer(self.__pixelsContainer)
    
    def nliGetChildren(self) -> Iterable['NamedLocalIdentifiable']|None:
        #if self._irRemote is not None:
        #    return [ self._irRemote ]
        return None
    
    def nliGetContainers(self) -> list["NamedLocalIdentifiableContainerMixin"]|None:
        return itertools.chain(  [ self.__pixelsContainer, self.__servoContainer ], super().nliGetContainers()) 

    def doRefresh(self,context:UpdateContext):
        for pixels in self.__allPixels:
            pixels.refresh()
        
    
    @property
    def pixels(self) -> NeoPixelSource: return self.__pixels
        
    @property
    def neoPixOnServo1(self) -> NeoPixelSource: return  self.__neoPixOnServos[0] 
    @property
    def neoPixOnServo2(self) -> NeoPixelSource: return  self.__neoPixOnServos[1] 
    @property
    def neoPixOnServo3(self) -> NeoPixelSource: return  self.__neoPixOnServos[2] 

    @property
    def servo1(self) -> LocalServo: return  self.__servos[0] 
    @property
    def servo2(self) -> LocalServo: return  self.__servos[1] 
    @property
    def servo3(self) -> LocalServo: return  self.__servos[2]
    
    def initNeoPixOnServo( self, servoN:int, 
                neoPixelCount:int = 1,
                name:str = None, 
                neoPixelOrder = neopixel.GRB,
                neoPixelBrightness = 0.2,
             ) -> NeoPixelSource:
        assert( self.__servos[servoN-1] is None  and self.__neoPixOnServos[servoN-1] is None )
        pin = self.config.option('servo{}pin'.format(servoN))
        name = name or f"pixel{servoN}"

        pixels = NeoPixelSource(
            pin, neoPixelCount, main = self.main, refreshRate=0.05,
                brightness=neoPixelBrightness, auto_write=False, pixel_order=neoPixelOrder
        )
        self.__neoPixOnServos[servoN-1] = pixels
        self.__allPixels.append(pixels)
        return pixels
    

    def addIrRemote(self, codenames:Mapping[str,int]|str|None = None) -> LCP_IRrecv:
        assert self._irRemote is None
        codenames = codenames or {
            "CH-": 0xffa25d,
            "CH": 0xff629d,
            "CH+": 0xffe21d,
            "PREV": 0xff22dd,
            "NEXT": 0xFF02FD,
            "PLAY": 0xffc23d,
            "VOL-": 0xffe01f,
            "VOL+": 0xffa857,
        }
        self._irRemote = LCP_IRrecv( self.D5.actualPin, codenames=codenames, main=self.main )
        self.nliAddComponent(self._irRemote)
        return self._irRemote
    
    def analogInput( self, name, pin ):
        return self.main.addInput( name, pin )
    
    def initServo( self, servoN:int, name:Optional[str] = None, duty_cycle:int = 2 ** 15, frequency=50, **kwds) -> LocalServo:
        ensure( self.__servos[servoN-1] is None, "servo position already in use by %r",  self.__servos[servoN-1] )
        ensure( self.__neoPixOnServos[servoN-1] is None, "servo position already in use by %r",  self.__neoPixOnServos[servoN-1]  )
        pin = self.config.option('servo{}pin'.format(servoN))
        name = name or f"servo{servoN}"
        pwm = pwmio.PWMOut( pin, duty_cycle=duty_cycle, frequency=frequency)
        servo = LocalServo(pwm,name, main=self.main, **kwds)
        servo.nliSetContainer(self.__servoContainer)
        self.__servos[servoN-1] = servo
        return servo
    


    
       