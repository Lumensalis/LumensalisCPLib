from TerrainTronics.Demos.DemoBase import DemoBase
from adafruit_simplemath import constrain
import displayio, terminalio

import adafruit_display_text.label
import adafruit_display_shapes.arc

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
        self.display = main.i2cFactory.addDisplayIO_SSD1306(128, 32, i2c=caernarfon.i2c)

        bitmap = displayio.OnDiskBitmap(open("TTLogo32.bmp", "rb"))
        image = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
        self.display.canvas.append(image) # shows the image


        self.statLabel = adafruit_display_text.label.Label(
            terminalio.FONT, text="---", color=0xFFFFFF, x=35, y=self.display.displayHeight // 2 - 1)
        
        self.display.canvas.append(self.statLabel)
        
        
        arcRadius = self.display.displayHeight / 4
        self.angleArc = adafruit_display_shapes.arc.Arc( radius = arcRadius,
                        angle = 90, direction=180, segments=7, arc_width=2,
                        fill = 0xFFFFFF )
        self.angleArc.x = self.display.displayWidth - int(arcRadius * 2.5)
        self.angleArc.y = int(arcRadius * 1.5)
        self.display.canvas.append(self.angleArc)

        
        dot_bitmap = displayio.Bitmap(1, 1, 1)
        dot_palette = displayio.Palette(1)
        dot_palette[0] = 0xFFFFFF # White
        self.dot_sprite = displayio.TileGrid(dot_bitmap, pixel_shader=dot_palette, x=0, y=0)
        self.display.canvas.append(self.dot_sprite)
        
        self.displayTargetPixel = [0,0]
        self.updateTextEveryNCycles = 10
        self.priorS1angle = 0
    
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

        # determine new location - wrapping based on cycle PLUS joystick position
        self.dot_sprite.x = int(main.cycle + nx*display.displayWidth) % display.displayWidth
        self.dot_sprite.y = int(main.cycle + ny*display.displayHeight) % display.displayHeight
        
        if self.priorS1angle != s1angle:
            self.priorS1angle!= s1angle
            self.angleArc.angle = -s1angle*2

        if main.cycle % self.updateTextEveryNCycles == 0:
            self.statLabel.text = f'{int(main.cycle/self.updateTextEveryNCycles)} {int(s1angle)}'



def demoMain(*args,**kwds):
    
    demo = CaernarfonFrankenDemo( *args, **kwds )
    demo.run()