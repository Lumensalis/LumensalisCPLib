from TerrainTronics.Demos.DemoBase import DemoBase
from LumensalisCP.Main.Terms import *
from LumensalisCP.Scenes.Scene import addSceneTask
from TerrainTronics.Caernarfon.Castle import onIRCode

from LumensalisCP.Triggers import Trigger, fireOnSet, fireOnTrue

from LumensalisCP.Audio import Audio
import board

class CaernarfonLogicDemo( DemoBase ):
    def setup(self):
        main = self.main
        
        audio = Audio( bit_clock=board.IO14,word_select= board.IO13, data=board.IO15 )

        sine_wave_sample = audio.makeSine()
        siren = audio.readSample("/assets/audio/NuclearSiren.mp3")
        boing = audio.readSample("/assets/audio/boing_spring.wav")
       
        # main.timers.dbgOutEnabled = True
        
        #############################################################################
        # Add a CaernarfonCastle
        NEO_PIXEL_COUNT = 40
        self.caernarfon = caernarfon = main.addCaernarfon( neoPixelCount=NEO_PIXEL_COUNT )

        ir = self.caernarfon.addIrRemote()

        ranger = main.i2cFactory.addVL530lx()
        
            
        doorDrive = caernarfon.initServo( 1, "doorDrive", )
        doorDrive.set( 45 )
        
        def doorUp(): 
            print( "raising the gate")
            doorDrive.moveTo(15, speed=15)
            
        def doorDown(): 
            print( "lowering the gate")
            doorDrive.moveTo(115, speed=30)
            

        ir.onCode( "CH+", doorUp )
        ir.onCode( "CH-", doorDown )
        

        magSensor = main.adafruitFactory.addTLV493D(name="MagCheck")

        @fireOnTrue( rising( magSensor.distance > 550, reset = magSensor.distance < 150 ) )
        def guardPresent():
            print( f"uh oh, guardPresent : {magSensor.distance.value}")
            doorDown()
        
        #guardPresent._onTrueExpression.dbgOutEnabled = True
        
        @fireOnTrue( rising( magSensor.distance < 250, reset = magSensor.distance > 400) )
        def guardLeft():
            print( f"uh oh, guardLeft : {magSensor.distance.value}" )
            doorUp()
      
        capTouch = main.adafruitFactory.addMPR121()
        touchy = capTouch.addInput( 0, "touchy" )
        
        touchy2 = capTouch.addInput( 2, "touchy2" )
        
        touched = Trigger("touched")
        

        @touched.fireOnSetDef( touchy )
        def foo():
            print( f"TOUCHED!!! touchy = {touchy.value}" )
            boing.play()
                    
        @touched.fireOnSetDef( touchy2 )
        def foo2():
            print( f"TOUCHED!!! touchy2 = {touchy2.value}" )
            boing.play()
                                    
        act1 = main.addScene( "firstAct" )

        ranger.checkRangerMode = 'startMeasurement'
        
        @addSceneTask( act1, period = 0.1 )
        def checkRanger():
            mode = getattr(ranger,'checkRangerMode', None)
            if mode is None or mode == 'startMeasurement':
                ranger.do_range_measurement()
                ranger.checkRangerMode = "measuring"
            elif ranger.checkRangerMode == "measuring":
                if ranger.data_ready:
                    range = ranger.range
                    ranger.checkRangerMode = "startMeasurement"
                    print( f"ranger range = {range}")
                    
        COLOR_CYCLE = 3.0
        NEO_PIXEL_SPREAD = 4
        pxStep = 1 / (NEO_PIXEL_COUNT *  NEO_PIXEL_SPREAD)


        #@addSceneTask( act1, period = 5.0 )
        def checkCap():
            def showPin( n ):
                c = capTouch[n]
                print( f"cap{n} {c.value} raw={c.raw_value} {c.release_threshold} {c.threshold} bl={capTouch.baseline_data(n)} flt={capTouch.filtered_data(n)}")
            showPin( 11 )
            showPin( 5 )
            showPin( 2 )
            showPin( 0 )

        @addSceneTask( act1, period = 0.01 )
        def rainbow():
            A =  main.seconds / COLOR_CYCLE
            
            # set each pixel
            for px in range(NEO_PIXEL_COUNT):
                caernarfon.pixels[px] = main.wheel1( A + (px * pxStep) )
                
            caernarfon.pixels.refresh()
        
        
        lightLevel = caernarfon.A0.addAnalogInput( "lightLevel" )
        doorSwitch = caernarfon.D5.addInput( "doorSwitch" )
        plateSensor = doorSwitch # caernarfon.D7.addInput( "plateSensor" )

        led_0 = caernarfon.D4.addOutput("led_0" )


        act1.addRule(  led_0, 
                     doorSwitch & ~plateSensor
                ).when( 
                    lightLevel > 35
                ).otherwise(
                    plateSensor 
                )
            
        # act1.addRule( caernarfon.servo1, TERM(20) + (MILLIS / 20)%160 )

        act2 = main.addScene( "secondAct" )
        # act2.addRule( caernarfon.servo1, TERM(20) + (MILLIS / 100)%160 )
        
        sceneManager = main.scenes
        
        
        

        
        @onIRCode( ir, 0xFF02FD )
        def next():
            newScene = sceneManager.currentScene
            if sceneManager.currentScene is act1:
                newScene = act2
            else:
                newScene = act1
            if newScene is not sceneManager.currentScene:
                print( f"switching to scene {newScene.name}")
                sceneManager.setScene( newScene )
            
        def checkRemote():
            ir.check()
            
        act1.addTask( checkRemote, period = 0.1 )
        act2.addTask( checkRemote, period = 0.1 )

        
        print(f"sources = {act1.sources()}" )

def demoMain(*args,**kwds):
    
    demo = CaernarfonLogicDemo( *args, **kwds )
    demo.run()