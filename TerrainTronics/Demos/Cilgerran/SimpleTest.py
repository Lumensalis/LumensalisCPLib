from TerrainTronics.Demos.DemoBase import *
from LumensalisCP.Lights.Patterns import *

class CilgerranSimpleTestDemo( DemoBase ):
    def setup(self):

        self.cilgerran = cilgerran = self.main.TerrainTronics.addCilgerran()
        scene = self.main.addScene( "simpleBlink" )

        #cilgerran.batteryMonitor.enableDbgOut = True

        leds = cilgerran.ledSource
        leds.addLeds(8)
        
        #firstTwo = leds.nextNLights(2)
        #firstFour = leds.nextNLights(2)
        lastFour = leds.nextNLights(8)

        
        scene.addPatterns(
            #Cylon(firstFour, sweepTime=0.7),
            Blink(lastFour,offTime=0.25),
        )

        BRIGHTNESS_SWEEP_SECONDS = 10.0
        @addSceneTask( scene, period = 0.1 )
        def brighten():
            brightness = (
                divmod( self.main.when, BRIGHTNESS_SWEEP_SECONDS )[1]
                    / BRIGHTNESS_SWEEP_SECONDS ) #/ 10.0
            
            print( f"brightness = {brightness}")
            leds.brightness = brightness

        @addSceneTask( scene, period = 10 )
        def showBatter():
            print( f"battery = {cilgerran.batteryMonitor.value}")


def demoMain(*args,**kwds):
    demo = CilgerranSimpleTestDemo( *args, **kwds )
    demo.run()