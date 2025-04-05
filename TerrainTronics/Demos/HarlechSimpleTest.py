from TerrainTronics.Demos.DemoBase import DemoBase
from LumensalisCP.Main.Terms import *
from LumensalisCP.Scenes.Scene import addSceneTask
import math

LED_COUNT = 8

class HarlechSimpleTestDemo( DemoBase ):
    def setup(self):

        self.harlech = harlech = self.main.addHarlech( )
        scene = self.main.addScene( "simpleBlink" )

        harlech.keepAlive.enableDbgOut = True
        #harlech.keepAlive._keepAliveTimer.enableDbgOut = True
        harlech.keepAlive._keepAliveTimer.dbgOut( "Can You Hear Me?" )
        print( f"or not? {harlech.keepAlive.enableDbgOut}")
        
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



def demoMain(*args,**kwds):
    demo = HarlechSimpleTestDemo( *args, **kwds )
    demo.run()