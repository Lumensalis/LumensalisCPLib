from TerrainTronics.Demos.DemoBase import *


class CaernarfonGateDemo( DemoBase ):
    def setup(self):
        main = self.main

        # main.timers.dbgOutEnabled = True
        
        #############################################################################
        # Add a CaernarfonCastle
        NEO_PIXEL_COUNT = 40
        self.caernarfon = caernarfon = main.addCaernarfon( neoPixelCount=NEO_PIXEL_COUNT )

        # add audio
        
        #sampleExt, audioKwds = "2232.mp3", dict(useMixer = True, mixer_sample_rate = 22050, mixer_signed = True)
        sampleExt, audioKwds = "22u8.wav", dict(useMixer = True, mixer_sample_rate = 22050, mixer_signed = False, mixer_bits_per_sample=8)
        
        audio = main.addI2SAudio( bit_clock=board.IO14,word_select= board.IO13, data=board.IO10,
                            #useMixer = True, mixer_sample_rate = 44100, mixer_signed = True
                            #useMixer = True, mixer_sample_rate = 22050, mixer_signed = True
                            **audioKwds
                        )
        audio.dbgOutEnabled = True
        audio.volume = 0.3
        

        warningSiren, nukeSiren = audio.readSamples(
                    "/assets/audio/WarningSiren" + sampleExt,
                    #"/assets/audio/NuclearSiren" + sampleExt,
                    "/assets/audio/WarningSiren" + sampleExt,
            )
        doorCloseSample, engineSample, grindingSample = audio.readSamples(
                    "/assets/audio/HeavyClose" + sampleExt,
                    "/assets/audio/engineLoop" + sampleExt,
                    "/assets/audio/grinding" + sampleExt,
                )

        if 0:        
            grindingSample, boing = audio.readSamples(
                    "/assets/audio/grinding" + sampleExt,
                    "/assets/audio/boing_spring.wav",
                )
       

        
        def stopSounds():
            audio.stop()
        
        #####################################################################
        # gate movement
        gateClosedPosition = 15
        gateOpenPosition = 115
        
        doorDrive = caernarfon.initServo( 1, "doorDrive", )
        doorDrive.set( 45 )
        def doorStopped():
            print( "door stopped" )
            audio.stop()
            grindingSample.play()

        def doorArrived():
            print( f"door arrived, angle={doorDrive.lastSetAngle}" )
            audio.stop()
            if doorDrive.lastSetAngle <= gateClosedPosition:
                doorCloseSample.play(level=0.75)
                #boing.play()
            elif doorDrive.lastSetAngle >= gateOpenPosition:
                doorCloseSample.play(level=0.75)
                #boing.play()
                
        doorDrive.onStop( doorStopped )
        doorDrive.onMoveComplete( doorArrived )
        
        def doorUp(): 
            print( "raising the gate")
            doorDrive.moveTo(gateClosedPosition, speed=15)
            engineSample.play(loop=True, level=0.5)
            
        def doorDown(): 
            print( "lowering the gate")
            doorDrive.moveTo(gateOpenPosition, speed=30)
            engineSample.play(loop=True, level=0.3)


        #####################################################################
        #  gate guard detection
        magSensor = main.adafruitFactory.addTLV493D(name="MagCheck")
        #magSensor.dbgOutEnabled = True

        onGuardDistance = 550
        leftDutyDistance = 250
        @fireOnTrue( rising( magSensor.distance > onGuardDistance, reset = magSensor.distance < leftDutyDistance ) )
        def guardPresent():
            print( f"uh oh, guardPresent : {magSensor.distance.value}")
            doorDown()
        
        @fireOnTrue( rising( magSensor.distance < leftDutyDistance, reset = magSensor.distance > onGuardDistance ) )
        def guardLeft():
            print( f"uh oh, guardLeft : {magSensor.distance.value}" )
            doorUp()
      

        ranger = main.i2cFactory.addVL530lx()
        # ranger.dbgOutEnabled = True


        #####################################################################
        ir = self.caernarfon.addIrRemote()
        
        ir.onCode( "CH+", doorUp )
        ir.onCode( "CH-", doorDown )

        @onIRCode( ir, "VOL+" )
        def increaseVolume():
            audio.volume += 0.1
            print( f"volume = {audio.volume*10:.1f}")
        
        @onIRCode( ir, "VOL-" )
        def decreaseVolume():
            audio.volume -= 0.1
            print( f"volume = {audio.volume*10:.1f}")
        
              
        #####################################################################

                                    
        act1 = main.addScene( "firstAct" )

        COLOR_CYCLE = 3.0
        NEO_PIXEL_SPREAD = 4
        pxStep = 1 / (NEO_PIXEL_COUNT *  NEO_PIXEL_SPREAD)


        circle8 = caernarfon.pixels.nextNLights(8)
        strip = caernarfon.pixels.nextNLights(10)
        
        gateFrontRange = ranger.range
        foo = main.addIntermediateVariable("foo", 0)
        
        
        act1.addRule(  foo, 
                gateFrontRange / 20
            ).when( 
                    gateFrontRange < 1000
            ).otherwise(
                TERM( 50 )
            )
        
        
        @addSceneTask( act1, period = 0.01 )
        def rainbow():
            #A =  (main.seconds + (gateFrontRange.value or 0)) / COLOR_CYCLE
            A =  (main.seconds + foo.value) / COLOR_CYCLE
            # set each pixel
            for px in range(strip.lightCount):
                strip[px] = main.wheel1( A + (px * pxStep) )
                
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
            

        capTouch = main.adafruitFactory.addMPR121()
        capTouch.dbgOutEnabled = True
        ct0 = capTouch.addInput( 0, "ct0" )
        ct2 = capTouch.addInput( 2, "ct2" )
        ct10 = capTouch.addInput( 10, "ct10" )
        ct10.dbgOutEnabled = True
        
        touched = Trigger("touched")
        touched.dbgOutEnabled = True
        
        @touched.addActionDef()
        def onTouched(**kwds):
            print( f"TOUCHED!!! ct0={ct0.value}, ct2={ct2.value}, ct10={ct10.value}" )
            if ct2.value:
                warningSiren.play()
            if ct10.value:
                nukeSiren.play()
        
        touched.fireOnSourcesSet(ct0,ct2,ct10)
                                       
        print(f"sources = {act1.sources()}" )

def demoMain(*args,**kwds):
    
    demo = CaernarfonGateDemo( *args, **kwds )
    demo.run()