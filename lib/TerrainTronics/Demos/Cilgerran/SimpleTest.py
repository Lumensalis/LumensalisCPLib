from LumensalisCP.Demo.DemoCommon import *
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
            Blink(lastFour,onTime=15.0, offTime=1.5),
        )
        leds.brightness = 1
        

        BRIGHTNESS_SWEEP_SECONDS = 10.0
        # @addSceneTask( scene, period = 0.1 )
        def brighten():
            brightness = (
                divmod( self.main.when, BRIGHTNESS_SWEEP_SECONDS )[1]
                    / BRIGHTNESS_SWEEP_SECONDS ) #/ 10.0
            
            print( f"brightness = {brightness}")
            leds.brightness = brightness

        @addSceneTask( scene, period = 5 )
        def showBattery():
            b = leds.brightness
            print( f"battery = {cilgerran.batteryMonitor.value}, brightness={b}")
            #print( f' leds={",".join( [repr(led) for led in leds])}')
            #leds.brightness = b
            


def demoMain(*args,**kwds):
    demo = CilgerranSimpleTestDemo( *args, **kwds )
    demo.run()