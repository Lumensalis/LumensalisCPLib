from .DemoCommon import *
from LumensalisCP.Lights.Patterns import *

LED_COUNT = 8
NEO_PIXEL_COUNT = 40
class TwinCastles( DemoBase ):
    def setup(self):

        main = self.main
        # main.timers.enableDbgOut = True

        harlech = harlech = self.main.addHarlech( )
        caernarfon = main.addCaernarfon( config="lolin_s2_mini_b", neoPixelCount=NEO_PIXEL_COUNT )


        self.harlech = harlech
        self.caernarfon = caernarfon 
        scene = self.main.addScene( "simpleBlink" )

        harlech.keepAlive.enableDbgOut = True
        #harlech.keepAlive._keepAliveTimer.enableDbgOut = True
        harlech.keepAlive._keepAliveTimer.dbgOut( "Can You Hear Me?" )
        print( f"or not? {harlech.keepAlive.enableDbgOut}")
        
        #####################################################################
        # Add a CaernarfonCastle



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
                
        
        return 



        #ranger = main.i2cFactory.addVL530lx()
        # ranger.enableDbgOut = True


        #####################################################################
        #ir = self.caernarfon.addIrRemote()
        
        #ir.onCode( "CH+", doorUp )
        #ir.onCode( "CH-", doorDown )

        #####################################################################

                                    
        scene = self.main.addScene( "simpleBlink" )
  
        circle8 = caernarfon.pixels.nextNLights(8)
        strip = caernarfon.pixels.nextNLights(10)
        
        harlech.brightness = 1.0
        leds = []
        for ledNumber in range(LED_COUNT):
            leds.append( harlech.led(ledNumber, "led{ledNumber}" ) )

        harlech.brightness = 1.1
        scene.blinkCycle = 0

        @addSceneTask( scene, period = 3.5 )
        def printStuff():
            print( f"blinkCycle={scene.blinkCycle}")
            timer = harlech.keepAlive._keepAliveTimer
            harlech.keepAlive.infoOut( f"HKAT running={timer.running}, lastFire={timer.lastFire} , nextFire={timer.nextFire}")
            print( f"Harlech shiftWrites={harlech._shiftWrites}, {harlech._gpio[0]:2.2X} ")
            
            
        @addSceneTask( scene, period = 0.5 )
        def blinkThem():
            scene.blinkCycle += 1
            
            #values = [((scene.blinkCycle % (x+2) ) == 0) for x in range(LED_COUNT)]
            values = ""
            for ledNumber in range(LED_COUNT):
                ledState = 1.0 if ( scene.blinkCycle % (ledNumber+1) ) <= (ledNumber+1)/2 else 0
                leds[ledNumber].set( ledState )
                values += '+' if ledState else '.'
            
            print( f"leds = {values}")

        BRIGHTNESS_SWEEP_SECONDS = 10.0
        #@addSceneTask( scene, period = 0.1 )
        def brighten():
            brightness = (
                divmod( self.main.when, BRIGHTNESS_SWEEP_SECONDS )[1]
                    / BRIGHTNESS_SWEEP_SECONDS ) #/ 10.0
            
            #print( f"brightness = {brightness}")
            harlech.brightness = brightness

        
        
        if 0:
            act1.addPatterns(
                Blink(circle8, onValue=0x800000,offTime=0.25),
                Rainbow(strip, name="rb", spread=2)
            )
        
        
 
        
        capTouch = main.adafruitFactory.addMPR121()
        capTouch.enableDbgOut = True
        ct0 = capTouch.addInput( 0, "ct0" )
        ct2 = capTouch.addInput( 2, "ct2" )
        ct10 = capTouch.addInput( 10, "ct10" )
        ct10.enableDbgOut = True
        
        touched = Trigger("touched")
        touched.enableDbgOut = True
        
        @touched.addActionDef()
        def onTouched(**kwds):
            print( f"TOUCHED!!! ct0={ct0.value}, ct2={ct2.value}, ct10={ct10.value}" )
        
        touched.fireOnSourcesSet(ct0,ct2,ct10)
                                       
        print(f"sources = {act1.sources()}" )

def demoMain(*args,**kwds):
    
    demo = TwinCastles( *args, **kwds )
    demo.run()