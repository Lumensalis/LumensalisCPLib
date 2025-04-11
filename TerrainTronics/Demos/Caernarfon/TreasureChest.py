from ..DemoCommon import *
from LumensalisCP.Lights.ProxyLights import DimmedLightsSource

class TreasureChest( DemoBase ):
    def setup(self):

        main = self.main


        #####################################################################
        # Add a CaernarfonCastle
        caernarfon = main.TerrainTronics.addCaernarfon( neoPixelCount=45 )
        pixels = caernarfon.pixels 
        #pixels._refreshRate
        
        pixOnCaernarfon = pixels.nextNLights(1)
        stripA = pixels.nextNLights(8)
        stoneA = DimmedLightsSource( pixels.nextNLights(3), 0.15 )
        stoneB = DimmedLightsSource( pixels.nextNLights(7), 0.2 )
        singleA = pixels.nextNLights(1)
        ringA = pixels.nextNLights(12)
        stripB  = pixels.nextNLights(8)
        

        
        pixels2 = caernarfon.initNeoPixOnServo(3,neoPixelCount=35)
        ringB = pixels2.nextNLights(16)
        ringC = pixels2.nextNLights(3)
        ringD = pixels2.nextNLights(7)
        
        display = self.main.i2cFactory.addDisplayIO_SSD1306(displayHeight=64)
        display.addBitmap( "/assets/bitmap/TTLogo32.bmp" )
        displayMidHeight = display.displayHeight // 2 - 1
        statField = display.addText( "---", x=35, y=displayMidHeight )
        potField = display.addText( "---", x=35, y=displayMidHeight + 12 )


        
        sceneClosed = main.addScene("closed")
        sceneOpen = main.addScene("open")
        sceneOpening = main.addScene("opening")
        sceneClosing = main.addScene("closing")
        
        def rChannel(): return randint(0,64)
        def randomRGB(): return (rChannel() << 16) + (rChannel() << 8) +  rChannel()
        

        #randomRingA = Random(ringA, duration = 0.25, brightness=0.3)
        
        #cylon2stripA = Cylon2(stripA,onValue=randomRGB,sweepTime=0.5)
            
        sceneClosed.addPatterns(
            #Rainbow(ringA),
            Rainbow(stoneA,colorCycle=5, spread=0.25),
            Rainbow(stoneB,colorCycle=1.5, spread=1),
            Blink(singleA, onValue=randomRGB,
                    onTime=lambda:randomZeroToOne() * 0.5,
                    offTime=lambda:randomZeroToOne() *3 
            ),
            #Blink(ringA, onValue=0x800000,offTime=0.25),
            #randomRingA,
            #Rainbow(ringB, spread=2),
            Random(ringA, duration = 0.1, brightness=0.2), # , intermediateRefresh=0.1
            Cylon2(stripA, onValue=0x800000 ),
            #cylon2stripA,
            #Rainbow(ringD),
       
            
            #Blink(ringC, onValue=randomRGB,onTime=0.25, offTime=0.25),
            
        )
        
        
        @sceneClosed.addTaskDef(period=0.1)
        def ml(**kwargs):
            pixels.refresh()

        @sceneClosed.addTaskDef(period=1)
        def ml2(**kwargs):
            #print( f"randomRingA = {randomRingA.stats()} / {ringA.values()}" )
            #print( f"cylon2stripA = {cylon2stripA.stats()} / {stripA.values()}" )
            #print( f"pixels  = {pixels.stats()}" )
            pass
            
        #####################################################################
        # gate movement
        lidClosedPosition = 123
        lidOpenPosition = 10
        lidOpenSpeed = 30
        lidCloseSpeed = 40
        
        lidDrive = caernarfon.initServo( 1, "lidDrive", )
        lidDrive.set(lidClosedPosition)

        def  lidArrived():
            print( "lid arrived, turning servo off" )
            lidDrive.set( None )
            
        lidDrive.onMoveComplete( lidArrived )
        #ranger = main.i2cFactory.addVL530lx()
        # ranger.enableDbgOut = True

        #####################################################################
        ir = caernarfon.addIrRemote()
        #####################################################################

        foo = main.addIntermediateVariable("foo", 0)

        sceneManager = main.scenes
        
        @ir.onCodeDef( "NEXT" )
        def next():
            newScene = dict(
                closed = sceneOpening,
                opening = sceneOpen,
                open = sceneClosing,
                closing = sceneClosed
            ).get( sceneManager.currentScene, None )

            if newScene is not sceneManager.currentScene:
                print( f"switching to scene {newScene.name}")
                sceneManager.setScene( newScene )
        
        @ir.onCodeDef( "CH-" )
        def closeLid():
            lidDrive.moveTo(lidClosedPosition,lidCloseSpeed)

        @ir.onCodeDef( "CH+" )
        def openLid():
            lidDrive.moveTo(lidOpenPosition,lidOpenSpeed)
            
        @ir.onCodeDef( "VOL+" )
        def jogLidUp():
            newAngle = lidDrive.lastSetAngle -1
            print( f"lid to {newAngle}")
            lidDrive.set(newAngle)

        @ir.onCodeDef( "VOL-" )
        def jogLidDown():
            newAngle = lidDrive.lastSetAngle +1
            print( f"lid to {newAngle}")
            lidDrive.set(newAngle)
                        
        if 1:
            capTouch = main.adafruitFactory.addMPR121()
            capTouch.enableDbgOut = True
            gemA = capTouch.addInput( 0, "a" )
            gemB = capTouch.addInput( 6, "b" )
            gemC = capTouch.addInput( 3, "c" )
            gemD = capTouch.addInput( 7, "d" )
            
            touched = Trigger("touched")
            touched.enableDbgOut = True
            
            @touched.addActionDef()
            def onTouched(**kwds):
                if gemA:
                    openLid()
                elif  gemB:
                    closeLid()
                elif gemC:
                    lidDrive.stop()
                    
                print( f"TOUCHED!!! { capTouch.touchedInputs}" )
                    
            print( f"capTouch.inputs = {capTouch.inputs}")
            touched.fireOnSourcesSet(*capTouch.inputs )
            
            def onUnusedTouch( unused=0, context=None ):
                activePins = []
                touched = capTouch.lastTouched
                for pin in range( capTouch.MPR121_PINS ):
                    if touched & (1 << pin):
                        activePins.append(pin)
                print( f"Unused Touch, touched={touched:X} pins = { ",".join([repr(pin) for pin in activePins])}")
            
            capTouch.onUnused( onUnusedTouch )
            
        print(f"sources = {sceneClosed.sources()}" )

def demoMain(*args,**kwds):
    
    demo = TreasureChest( *args, **kwds )
    demo.run()