
from TerrainTronics.Demos.DemoCommon import *

class CaernarfonSimpleDemo( DemoBase ):
    def setup(self):
        main = self.main
        
        caernarfon = self.main.TerrainTronics.addCaernarfon( neoPixelCount=40 )
        
        bigRing     =  caernarfon.pixels.nextNLights(32)
        littleStick =  caernarfon.pixels.nextNLights(8)
        
        irReceiver  = caernarfon.addIrRemote()
        servo1      = caernarfon.initServo( 1,"servo1" )
        servo2      = caernarfon.initServo( 2,"servo1" )
        
        capTouch    = caernarfon.adafruitFactory.addMPR121()
        rotary      = caernarfon.adafruitFactory.addQTRotaryEncoder(caernarfon.i2c)
        
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