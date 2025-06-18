from .DemoCommon import *
from LumensalisCP.Lights.Patterns import *

LED_COUNT = 8
NEO_PIXEL_COUNT = 40

class TwinCastles( DemoBase ):
    def setup(self):

        main = self.main
        # main.timers.enableDbgOut = True

        #####################################################################
        # Add a Harlech Castle on primary D1Mini pinout
        harlech = main.TerrainTronics.addHarlech( )
        self.harlech = harlech

        #####################################################################
        # Add a CaernarfonCastle on secondary D1Mini pinout
        caernarfon = main.TerrainTronics.addCaernarfon( config="secondary", neoPixelCount=NEO_PIXEL_COUNT )
        self.caernarfon = caernarfon
         
        scene = self.main.addScene( "simpleBlink" )

        doorDrive = caernarfon.initServo( 1, "doorDrive", )

        leds = []
        for ledNumber in range(LED_COUNT):
            leds.append( harlech.led(ledNumber, "led{ledNumber}" ) )

        scene.blinkCycle = 0

        #@addSceneTask( scene, period = 3.5 )
        def printStuff():
            print( f"blinkCycle={scene.blinkCycle}")
            timer = harlech.keepAlive._keepAliveTimer
            harlech.keepAlive.infoOut( f"HKAT running={timer.running}, lastFire={timer.lastFire} , nextFire={timer.nextFire}")
            
        @addSceneTask( scene, period = 0.5 )
        def blinkThem():
            scene.blinkCycle += 1
            
            #values = [((scene.blinkCycle % (x+2) ) == 0) for x in range(LED_COUNT)]
            #values = ""
            for ledNumber in range(LED_COUNT):
                ledState = ( scene.blinkCycle % (ledNumber+1) ) <= (ledNumber+1)/2 
                leds[ledNumber].set( ledState )
                #values += '+' if ledState else '.'
            
            #print( f"leds = {values}")

        BRIGHTNESS_SWEEP_SECONDS = 10.0
        @addSceneTask( scene, period = 0.1 )
        def brighten():
            brightness = (
                divmod( self.main.when, BRIGHTNESS_SWEEP_SECONDS )[1]
                    / BRIGHTNESS_SWEEP_SECONDS ) #/ 10.0
            
            #print( f"brightness = {brightness}")
            harlech.brightness = brightness

        circle8 = caernarfon.pixels.nextNLights(8)
        strip = caernarfon.pixels.nextNLights(10)
        
        scene.addPatterns(
                Blink(circle8, onValue=0x800000,offTime=0.25),
                Rainbow(strip, name="rb", spread=2)
            )

def demoMain(*args,**kwds):
    
    demo = TwinCastles( *args, **kwds )
    demo.run()