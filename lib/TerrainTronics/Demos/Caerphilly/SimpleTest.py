from LumensalisCP.Demo.DemoCommon import *
from LumensalisCP.Lights.Patterns import *

class CaerphillySimpleTestDemo( DemoBase ):
    def setup(self):

        caerphilly = self.main.TerrainTronics.addCaerphilly(neoPixelCount = 30)
        scene = self.main.addScene( "simpleBlink" )
        circle8A =  caerphilly.pixels.nextNLights(8)
        
        try:
            harlechXL = self.main.TerrainTronics.addHarlechXL()
        except Exception as inst:
            SHOW_EXCEPTION( inst, "hxl exception")
            caerphilly.scanI2C()
        
        bankA = harlechXL.nextNLights(8)
        scene.addPatterns( Blink( bankA, onValue=0.1 ) )

        bankB = harlechXL.nextNLights(8)
        bankC = harlechXL.nextNLights(8)
        bankD = harlechXL.nextNLights(8)
        
        rainbow = Rainbow(circle8A)
        
        
        scene.addPatterns(
                        rainbow,
                          Cylon(bankB),
                          Random(bankC,duration=0.2),
                          Blink(bankD),
                          )
        
        harlechXL.checkOpenShort()
        
        ir = caerphilly.addIrRemote()
        @ir.onCodeDef( "PLAY")
        def play():
            print( "PLAY...." )
            for led in harlechXL.lights:
                print( f"led {led.sourceIndex} : {led.value} : {led._driverValue}")

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


        @ir.onCodeDef( "VOL+")
        def brighter():
            harlechXL.brightness = min(1.0, harlechXL.brightness +0.1)

        @ir.onCodeDef( "VOL-")
        def dimmer():
            harlechXL.brightness = max(0.1, harlechXL.brightness - 0.1)

        @scene.addTaskDef( period=0.1 )
        def updateColorCycle(**kwargs):
            pot.getValue(self.main.latestContext)
            rainbow.colorCycle = pot.value / 5000.0
        
        @scene.addTaskDef( period=1.0 )
        def updatePotLabel(context=None,**kwargs):
            potField.text = f"{pot.value}"
            
        
def demoMain(*args,**kwds):
    demo = CaerphillySimpleTestDemo( *args, **kwds )
    demo.run()