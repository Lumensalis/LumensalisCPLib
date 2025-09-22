

import adafruit_seesaw
import adafruit_seesaw.seesaw
import adafruit_seesaw.rotaryio
import adafruit_seesaw.digitalio
import adafruit_seesaw.neopixel

from LumensalisCP.IOContext import *
from LumensalisCP.I2C.I2CDevice import  *

class QtRotary(I2CDevice):
    def __init__(self, *args:Any, **kwds:Unpack[I2CDevice.KWDS] ) -> None:
        super().__init__( *args, **kwds )
        # self.i2c = i2c # busio.I2C( microcontroller.pin.GPIO35, microcontroller.pin.GPIO33 ) 
        
        self.seesaw = adafruit_seesaw.seesaw.Seesaw(self.i2c, 0x36)
        self.encoder = adafruit_seesaw.rotaryio.IncrementalEncoder(self.seesaw)
        self.seesaw.pin_mode(24, self.seesaw.INPUT_PULLUP) # type: ignore
        self.switch = adafruit_seesaw.digitalio.DigitalIO(self.seesaw, 24)
        self.pixel = adafruit_seesaw.neopixel.NeoPixel(self.seesaw, 6, 1)
        self.pixel.brightness = 0.5
        self.last_button:bool = self.switch.value # type: ignore
        self.last_position:int = self.encoder.position # type: ignore
        self.color = 0  # start at red
        self.moveCB:Callable[[int],None]|None = None
        self.buttonCB:Callable[[bool],None]|None = None
    
    def onMove(self,cb:Callable[[int],None]):
        self.moveCB = cb

    def onButton(self,cb:Callable[[bool],None]):
        self.buttonCB = cb
    
        
    def updateStemmaEncoder(self):
        position= -cast(int,self.encoder.position) # type: ignore
        assert isinstance(position, int)
        if position != self.last_position:
            delta = position - self.last_position
            self.last_position = position
            if self.moveCB is not None:
                self.moveCB(delta)

        button = cast(bool, self.switch.value) # type: ignore
        
        if button != self.last_button:
            self.last_button = button
            if self.buttonCB is not None:
                self.buttonCB( button )
 
        self.last_position = position
