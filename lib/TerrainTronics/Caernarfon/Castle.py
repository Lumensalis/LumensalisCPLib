from __future__ import annotations

from LumensalisCP.IOContext import *
from LumensalisCP.commonCP import *
from LumensalisCP.Lights.NeoPixels import NeoPixelSource, NeoPixelSourceKwds
from LumensalisCP.Gadgets.IrRemote import LCP_IRrecv, onIRCode # type: ignore
from LumensalisCP.Gadgets.Servos import LocalServo

from TerrainTronics.D1MiniBoardBase import D1MiniBoardBase

class CaernarfonCastleKWDS(TypedDict):
        neoPixelCount: NotRequired[int]
        servos: NotRequired[int]
        servo1pin: NotRequired[microcontroller.Pin|str]
        servo2pin: NotRequired[microcontroller.Pin|str]
        servo3pin: NotRequired[microcontroller.Pin|str]

class CaernarfonCastle(D1MiniBoardBase):
    
    __servoContainer:NliList[LocalServo]
    __pixelsContainer:NliList[NeoPixelSource]
    class KWDS(D1MiniBoardBase.KWDS):
        neoPixelCount: NotRequired[int]
        servos: NotRequired[int]
        servo1pin: NotRequired[microcontroller.Pin|str]
        servo2pin: NotRequired[microcontroller.Pin|str]
        servo3pin: NotRequired[microcontroller.Pin|str]

    def __init__(self,
                neoPixelCount:int=0,
                servos:int=0,
                servo1pin: Optional[microcontroller.Pin] = None,
                servo2pin: Optional[microcontroller.Pin] = None,
                servo3pin: Optional[microcontroller.Pin] = None,
                neoPixels: Optional[NeoPixelSource.KWDS] = None,
                 **kwds:Unpack[D1MiniBoardBase.KWDS] 
             ) -> None:
        super().__init__( **kwds )
        c = self.config
        self._irRemote = None
        self.initI2C()
        
        self.__servoContainer = NliList("servos", parent=self)
        self.__servos:list[LocalServo|None] = [ None, None, None ]
        self.__neoPixOnServos:list[NeoPixelSource|None] = [ None, None, None ]
        self.__pixelsContainer  = NliList("pixels", parent=self)
        self.__allPixels: list[NeoPixelSource] = []
        
        self.servo1pin =  c.D6
        self.servo2pin =  c.D7
        self.servo3pin =  c.D8
        self.neoPixelPin = c.D3
        
        if neoPixelCount > 0:
            assert neoPixels is None
            self.addNeoPixels( pixelCount = neoPixelCount )
            
            #self.__pixels:NeoPixelSource = NeoPixelSource(
            #    c.neoPixelPin, pixelCount=c.neoPixelCount, main = self.main, refreshRate=0.05, 
                #brightness=c.neoPixelBrightness, 
             #   auto_write=False, pixel_order=c.neoPixelOrder # type: ignore
            #)
            #self.__pixels.nliSetContainer(self.__pixelsContainer)
    
    def addNeoPixels(self,
                    servoPin:Optional[int]=None, 
                    **kwds:Unpack[NeoPixelSourceKwds]
            ) -> NeoPixelSource:
        """ Add a NeoPixelSource chain to the Caernarfon Castle board.

        :param servoPin: If provided, the chain use the 
            specified servo channel. Otherwise, it will be added at the 
                board's NeoPixel connection

        see :class:`NeoPixelSource` for more details on the parameters.

        """
        pin = self.neoPixelPin if servoPin is None else getattr(self, f'servo{servoPin}pin')
        assert isinstance(pin, microcontroller.Pin)
        if servoPin is not None:
            ensure( self.__neoPixOnServos[servoPin-1] is None, "servo position already in use by %r",  self.__neoPixOnServos[servoPin-1]  )
        else:
            ensure( getattr(self,'__pixels',None) is None, "pixels already initialized" )
            
        kwds.setdefault( 'pixelCount', 1 )
        kwds.setdefault( 'pixel_order', neopixel.GRB ) # type: ignore

        pixels = NeoPixelSource( pin,  main = self.main,  **kwds )
        if servoPin is not None:
            self.__neoPixOnServos[servoPin-1] = pixels
        else:
            self.__pixels = pixels
            
        pixels.nliSetContainer(self.__pixelsContainer)
        self.__allPixels.append(pixels)
        return pixels

            #// refreshRate=0.05, brightness=neoPixelBrightness, auto_write=False, pixel_order=neoPixelOrder

    def initNeoPixOnServo( self, servoN:int, **kwds:Unpack[NeoPixelSourceKwds] ) -> NeoPixelSource:
        """Initialize a servo on one of the Caernarfon Castle's three Servo connections.

        :param servoN: which servo connection (1, 2, or 3)
        :type servoN: int
        :param kwds: additional keyword arguments for NeoPixelSource
        :return: the initialized NeoPixelSource instance
        """
        assert( self.__servos[servoN-1] is None  and self.__neoPixOnServos[servoN-1] is None )
        pin = getattr(self,f'servo{servoN}pin',None)
        assert isinstance(pin, microcontroller.Pin), f"servo{servoN}pin is not a pin: {pin}"

        pixels = NeoPixelSource( pin, main = self.main, **kwds )
        self.__neoPixOnServos[servoN-1] = pixels
        self.__allPixels.append(pixels)
        return pixels
    
        
    def nliGetChildren(self) -> Iterable['NamedLocalIdentifiable']|None:
        #if self._irRemote is not None:
        #    return [ self._irRemote ]
        return None
    
    def nliGetContainers(self) -> list["NliContainerMixin"]|None: # type: ignore
        return itertools.chain(  [ self.__pixelsContainer, self.__servoContainer ], super().nliGetContainers())  #type: ignore

    def doRefresh(self,context:EvaluationContext):
        for pixels in self.__allPixels:
            pixels.refresh()
        
    
    @property
    def pixels(self) -> NeoPixelSource: return self.__pixels
        
    @property
    def neoPixOnServo1(self) -> NeoPixelSource: 
        assert self.__neoPixOnServos[0] is not None
        return  self.__neoPixOnServos[0] 
    @property
    def neoPixOnServo2(self) -> NeoPixelSource: 
        assert self.__neoPixOnServos[1] is not None
        return  self.__neoPixOnServos[1] 
    @property
    def neoPixOnServo3(self) -> NeoPixelSource: 
        assert self.__neoPixOnServos[2] is not None
        return  self.__neoPixOnServos[2] 

    @property
    def servo1(self) -> LocalServo: 
        assert self.__servos[0] is not None
        return  self.__servos[0] 
    @property
    def servo2(self) -> LocalServo: 
        assert self.__servos[1] is not None
        return  self.__servos[1] 
    @property
    def servo3(self) -> LocalServo:
        assert self.__servos[2] is not None
        return  self.__servos[2]
    


    def addIrRemote(self, codenames:dict[str,int]|str|None = None) -> LCP_IRrecv:
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
        self._irRemote = LCP_IRrecv( self.D5.actualPin, main=self.main, codenames=codenames )
        self.nliAddComponent(self._irRemote)
        return self._irRemote
    
    #def analogInput( self, name:str, pin:Any ):
    #    return self.main.addInput( name, pin )
    
    def initServo( self, servoN:int, 
                  #//name:Optional[str] = None, 
                  duty_cycle:int = 2 ** 15,
                  frequency:int=50, 
                  **kwds:Unpack[LocalServo.KWDS]
                  ) -> LocalServo:
        """Initialize a servo on one of the Caernarfon Castle's three Servo connections.

        :param servoN: which servo connection (1, 2, or 3)
        :type servoN: int
        :param duty_cycle: the duty cycle for the servo, defaults to 2**15
        :type duty_cycle: int, optional
        :param frequency: the frequency for the servo, defaults to 50
        :type frequency: int, optional
        :return: the initialized LocalServo instance
        :rtype: LocalServo
        """
        ensure( self.__servos[servoN-1] is None, "servo position already in use by %r",  self.__servos[servoN-1] )
        ensure( self.__neoPixOnServos[servoN-1] is None, "servo position already in use by %r",  self.__neoPixOnServos[servoN-1]  )
        pin = getattr(self, 'servo{}pin'.format(servoN) )
        kwds.setdefault('name', f"servo{servoN}")
        pwm = pwmio.PWMOut( pin, duty_cycle=duty_cycle, frequency=frequency)
        servo = LocalServo(pwm, main=self.main, **kwds)
        servo.nliSetContainer(self.__servoContainer)
        self.__servos[servoN-1] = servo
        return servo
    


    
       