
from rainbowio import colorwheel
import adafruit_seesaw
import adafruit_seesaw.seesaw
import adafruit_seesaw.rotaryio
import adafruit_seesaw.digitalio
import adafruit_seesaw.neopixel


class QtRotary(object):
    def __init__(self, i2c):
        self.i2c = i2c # busio.I2C( microcontroller.pin.GPIO35, microcontroller.pin.GPIO33 ) 
        self.seesaw = adafruit_seesaw.seesaw.Seesaw(self.i2c, 0x36)
        self.encoder = adafruit_seesaw.rotaryio.IncrementalEncoder(self.seesaw)
        self.seesaw.pin_mode(24, self.seesaw.INPUT_PULLUP)
        self.switch = adafruit_seesaw.digitalio.DigitalIO(self.seesaw, 24)
        self.pixel = adafruit_seesaw.neopixel.NeoPixel(self.seesaw, 6, 1)
        self.pixel.brightness = 0.5
        self.last_button = self.switch.value
        self.last_position = self.encoder.position
        self.color = 0  # start at red
        self.moveCB = None
        self.buttonCB = None
    
    def onMove(self,cb):
        self.moveCB = cb
    
    def onButton(self,cb):
        self.buttonCB = cb
    
        
    def updateStemmaEncoder(self):
        position = -self.encoder.position
    
        if position != self.last_position:
            delta = position - self.last_position
            self.last_position = position
            if self.moveCB is not None:
                self.moveCB(delta)

        button = self.switch.value
        if button != self.last_button:
            self.last_button = button
            if self.buttonCB is not None:
                self.buttonCB( button )
            
        if 0:
            print(position)
    
            if self.switch.value:
                # Change the LED color.
                if position > self.last_position:  # Advance forward through the colorwheel.
                    self.color += 1
                else:
                    self.color -= 1  # Advance backward through the colorwheel.
                self.color = (self.color + 256) % 256  # wrap around to 0-256
                self.pixel.fill(colorwheel(self.color))
    
            else:  # If the button is pressed...
                # ...change the brightness.
                if position > self.last_position:  # Increase the brightness.
                    self.pixel.brightness = min(1.0, self.pixel.brightness + 0.1)
                else:  # Decrease the brightness.
                    self.pixel.brightness = max(0, self.pixel.brightness - 0.1)
    
        self.last_position = position
