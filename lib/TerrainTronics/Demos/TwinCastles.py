from LumensalisCP.Demo.DemoCommon import *
import wifi
LED_COUNT = 8
NEO_PIXEL_COUNT = 40

class TwinCastles( DemoBase ):
    def setup(self):

        main = self.main
        # main.timers.enableDbgOut = True
        #main.addBasicWebServer()
        #####################################################################
        # Add a Harlech Castle on primary D1Mini pinout
        #harlech = main.TerrainTronics.addHarlech( )
        #self.harlech = harlech

        #####################################################################
        # Add a CaernarfonCastle on secondary D1Mini pinout
        self.caernarfon = caernarfon = main.TerrainTronics.addCaernarfon( 
                config="secondary", 
                neoPixelCount=NEO_PIXEL_COUNT,
                refreshRate = 0.05
        )
        caernarfon.pixels.refreshRate = 0.05 
         
        self.ir =  ir = caernarfon.addIrRemote()
        ir.showUnhandled = True
        ir.enableDbgOut = True
    
        scene = self.main.addScene( "simpleBlink" )

        c1 = caernarfon.pixels.nextNLights(1)
        ringC = caernarfon.pixels.nextNLights(16)
        stripA = caernarfon.pixels.nextNLights(8)
        
        #self.dmx = main.dmx
        #dmxA = main.dmx.addDimmerInput( "a", 1 )
        #dmxB = main.dmx.addRGBInput( "b", 2 )
        
        
        scene.addPatterns(
                Rainbow(stripA, name="rb2", spread=3.5, colorCycle=1.4),
            )
        
        if 1:
            ringB = caernarfon.pixels.nextNLights(3)
            ringA = caernarfon.pixels.nextNLights(6)
            scene.addPatterns(
                Cylon2(ringA,),
                Blink(ringB, onValue=0x804020,offTime=0.25,onTime=0.25),
                Cylon2(ringC, ),
                #Rainbow(ringC,  spread=1.4, colorCycle=0.35),
            )
        
        if 0:
            hxl =  main.TerrainTronics.addHarlechXL(i2c=caernarfon.i2c)
            reds = hxl.nextNLights(8)
            scene.addPatterns(
                Rainbow(stripA, name="rb2", spread=1.4, colorCycle=0.35),
            )

        #doorDrive = caernarfon.initServo( 1, "doorDrive", )

        #@scene.addTaskDef(period=0.25)
        def dump():
            import json
            timings = dict(
                i= main.latestContext.updateIndex,
                timings =  main.dumpLoopTimings(10,minE=0.07) 
            )
            print( json.dumps( timings ) )
            
        #dt = PeriodicTimer( 3.1, manager=main.timers, name="dump" )
        #dt.addAction( dump )
        #dt.start()
        

    def __nope(self):

        leds = []
        for ledNumber in range(LED_COUNT):
            leds.append( harlech.led(ledNumber, "led{ledNumber}" ) )

        scene.blinkCycle = 0

        #@addSceneTask( scene, period = 0.5 )
        def printStuff(context=None):
            print( f"blinkCycle={scene.blinkCycle} dmxA={dmxA.getValue(context=context)} dmxB={dmxB.getValue(context=context)} ip={wifi.radio.ipv4_address}")
            #timer = harlech.keepAlive._keepAliveTimer
            #harlech.keepAlive.infoOut( f"HKAT running={timer.running}, lastFire={timer.lastFire} , nextFire={timer.nextFire}")
            
        #@addSceneTask( scene, period = 0.5 )
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
        #@addSceneTask( scene, period = 0.1 )
        def brighten():
            brightness = (
                divmod( self.main.when, BRIGHTNESS_SWEEP_SECONDS )[1]
                    / BRIGHTNESS_SWEEP_SECONDS ) #/ 10.0
            
            #print( f"brightness = {brightness}")
            harlech.brightness = brightness


def demoMain(*args,**kwds):
    
    demo = TwinCastles( *args, **kwds )
    demo.run()