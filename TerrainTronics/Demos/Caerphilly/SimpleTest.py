from TerrainTronics.Demos.DemoBase import *
from LumensalisCP.Lights.Patterns import *
import displayio, terminalio

import adafruit_display_text.label

class CaerphillySimpleTestDemo( DemoBase ):
    def setup(self):

        caerphilly = self.main.TerrainTronics.addCaerphilly(neoPixelCount = 30)
        scene = self.main.addScene( "simpleBlink" )
        circle8A =  caerphilly.pixels.nextNLights(8)
        
        scene.addPatterns(
            Rainbow(circle8A),
        )
        
        ir = caerphilly.addIrRemote()
        @ir.onCodeDef( "PLAY")
        def play():
            print( "PLAY...." )
            
        
        self.display = display = self.main.i2cFactory.addDisplayIO_SSD1306(displayHeight=64)
        display.addBitmap( "/assets/bitmap/TTLogo32.bmp" )
        displayMidHeight = self.display.displayHeight // 2 - 1
        statField = display.addText( "---", x=35, y=displayMidHeight )
        potField = display.addText( "---", x=35, y=displayMidHeight + 12 )
        
        
        @ir.onUnhandledDef()
        def unhandledIR( code:int = 0, **kwargs ):
            print( f"unhandledIR 0x{code:X}..." )
            statField.text = f"IR 0x{code:X}"

        pot = caerphilly.analogInput("pot")
        
        @scene.addTaskDef( period=1.0 )
        def updatePotLabel(context=None,**kwargs):
            pot.getValue(self.main.latestContext)
            potField.text = f"{pot.value}"
        
def demoMain(*args,**kwds):
    demo = CaerphillySimpleTestDemo( *args, **kwds )
    demo.run()