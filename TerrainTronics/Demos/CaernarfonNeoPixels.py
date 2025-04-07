
from TerrainTronics.Demos.DemoBase import *
from LumensalisCP.Lights.Patterns import *

class CaernarfonNeoPixelsDemo( DemoBase ):
    def setup(self):
        main = self.main
        
        # main.timers.enableDbgOut = True
        
        #############################################################################
        # Add a CaernarfonCastle
        NEO_PIXEL_COUNT = 40

        self.caernarfon = caernarfon = main.addCaernarfon( neoPixelCount=NEO_PIXEL_COUNT )
        pixels2 = caernarfon.initNeoPixOnSCaernarfon ervo( 2, 23 )
        
        pixels = caernarfon.pixels
        
        circle8A =  pixels.nextNLights(8)
        stickA =    pixels.nextNLights(8)
        stripA =    pixels.nextNLights( 5 )
        stickB =    pixels2.nextNLights(8)
        stickB2 =   pixels2.nextNLights(8)
        stripB =    pixels2.nextNLights(6)

        act1 = main.addScene( "firstAct" )

        cyp = Cylon(stickB, sweepTime=0.7, onValue=0xFF0000)
        act1.addPatterns(
            Blink(circle8A, onValue=0x800000,offTime=0.25),
            cyp,
            Rainbow(stickA, name="rb2", spread=3, colorCycle=3.2),
            Rainbow(stickB2, colorCycle=0.7),
            Rainbow(stripB, colorCycle=0.7),
        )
        

        act2 = main.addScene( "secondAct" )
        # act2.addRule( caernarfon.servo1, TERM(20) + (MILLIS / 100)%160 )
        
        sceneManager = main.scenes
        
        
        #####################################################################
        if 0:
            ir = self.caernarfon.addIrRemote()
            #def checkRemote(): ir.check()
            #act1.addTask( checkRemote, period = 0.1 )
            #act2.addTask( checkRemote, period = 0.1 )
            
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
            
        #####################################################################

        try:
            ranger = main.i2cFactory.addVL530lx()
            rangeDump = dict( rMin = 99999, rMax = 0, rMaxB = 1, rMaxBCap=2192, rCount = 0 )
            @addSceneTask( act1, period = 0.1 )
            def updateCylonColor():
                context = main.latestContext
                range = ranger.range.getValue(context=context) 
                showDump = ((rangeDump['rCount'] % 10) == 0)
                rangeDump['rCount'] += 1
                if range > rangeDump['rMax']: 
                    rangeDump['rMax'] = range
                    showDump = True
                if range > rangeDump['rMaxB'] and range < rangeDump['rMaxBCap']: 
                    rangeDump['rMaxB'] = range
                    showDump = True
                if range < rangeDump['rMin']: 
                    rangeDump['rMin'] = range
                    showDump = True
                    
                cyp.onValue = wheel1( range / rangeDump['rMaxB'] )
                if showDump:
                    print( f"range = {range}, {rangeDump}")
                
        except Exception as inst:
            caernarfon.SHOW_EXCEPTION( inst, "could not setup ranger")
        
        capTouch = main.adafruitFactory.addMPR121()
        touchy = capTouch.addInput( 0, "touchy" )
        
        touchy2 = capTouch.addInput( 2, "touchy2" )
        
        touched = Trigger("touched")
        

        @touched.fireOnSetDef( touchy )
        def foo():
            print( f"TOUCHED!!! touchy = {touchy.value}" )
                    
        @touched.fireOnSetDef( touchy2 )
        def foo2():
            print( f"TOUCHED!!! touchy2 = {touchy2.value}" )
                                    
 
        print(f"sources = {act1.sources()}" )

def demoMain(*args,**kwds):
    
    demo = CaernarfonNeoPixelsDemo( *args, **kwds )
    demo.run()