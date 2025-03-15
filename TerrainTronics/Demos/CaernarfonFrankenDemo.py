from TerrainTronics.Main import MainManager
from .DemoBase import DemoBase

from adafruit_simplemath import constrain


class CaernarfonFrankenDemo( DemoBase ):
    def __init__(self, *args, **kwds):
        super().__init__(*args,**kwds)
    
    def setup(self):
        main = self.main
        #############################################################################
        # ControlVariables are used to specify logical inputs which have their
        # values published to the WebUI and can be modified
        # by various control inputs (encoder movement, WebUI, ... )

        self.targetAngle = main.addControlVariable( "angle", "Servo Angle", min=20, max=160, kind="int" )
        self.targetColor = main.addControlVariable( "color", "Pixel Strip Color", kind="RGB", startingValue=(255,0,0) )

        #############################################################################
        # Add a CaernarfonCastle
        self.caernarfon = caernarfon = main.addCaernarfon( neoPixelCount=9, servos=1 )

        #############################################################################
        # I2C devices 

        # add an Adafruit QTRotaryEncoder, and set it up to adjust targetAngle
        self.qtr = main.adafruitFactory.createQTRotaryEncoder(caernarfon.i2c)
        self.qtr.onMove( self.encoderChanged )

        # add a WII Nunchuk
        self.nunchuk = main.adafruitFactory.createNunchuk(caernarfon.i2c)

        # add a display
        self.display = main.i2cFactory.addDisplay_SSD1306(128, 32, caernarfon.i2c)

        self.displayTargetPixel = [0,0]
        self.updateTextEveryNCycles = 10
    
    #########################################################################

    def encoderChanged(self, delta): 
        self.targetAngle.move( delta )
        print( f"targetAngle now {self.targetAngle.value}")


    def setDisplayPixel( self, state, location ):
        self.display.pixel( location[0], location[1], state )

    #########################################################################

    def singleLoop(self):
        main = self.main
        caernarfon = self.caernarfon
        
        # nx and ny will be the WII Nunchuck joystick position from -1.0 to 1.0
        nx, ny = self.nunchuk.scaledJoystick

        # change color on neopixel strip - 
        #  main.cycle increments automatically on every loop
        wheelTargetBase =  main.millis / 25 + nx*30
        pxOffset =-255/caernarfon.pixels.n 
        for px in range(caernarfon.pixels.n):
            caernarfon.pixels[px] = main.wheel( wheelTargetBase + (px * pxOffset) )
        caernarfon.pixels.show()

        # set LED on QTRotaryEncoder - targetColor changed via Web UI
        self.qtr.pixel.fill(self.targetColor.value)
        self.qtr.updateStemmaEncoder()

        # update servo - angle must stay within range to avoid exceptions
        s1angle = constrain( 
                self.targetAngle.value + ( (ny * 40) if self.nunchuk.buttons.C else 0),
                20, 160
            )
        caernarfon.servo1.angle = s1angle

        #update display
        display = self.display
        displayTargetPixel = self.displayTargetPixel
        if main.cycle % self.updateTextEveryNCycles == 0:
            display.fill(0)
            display.text(f'{int(main.cycle/self.updateTextEveryNCycles)} {int(s1angle)}', 0, 0, 1, size=2 )
        else:
            # clear the pixel we set last loop
            self.setDisplayPixel( 0, displayTargetPixel )

        # determine new location - wrapping based on cycle PLUS joystick position
        displayTargetPixel[0] = int(main.cycle + nx*display.displayWidth) % display.displayWidth
        displayTargetPixel[1] = int(main.cycle + ny*display.displayHeight) % display.displayHeight
        self.setDisplayPixel( 1, displayTargetPixel )

        display.show()


def demoMain(*args,**kwds):
    
    demo = CaernarfonFrankenDemo( *args, **kwds )
    demo.run()