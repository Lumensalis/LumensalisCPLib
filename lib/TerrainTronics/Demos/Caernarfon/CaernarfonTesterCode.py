
from LumensalisCP.Demo.DemoCommon import *
from LumensalisCP.Lights.Patterns import *

class CaernarfonTester( DemoBase ):
    def setup(self):
        main = self.main
        
        # main.timers.enableDbgOut = True
        
        #############################################################################
        # Add a CaernarfonCastle
        NEO_PIXEL_COUNT = 40

        self.caernarfon = caernarfon = main.TerrainTronics.addCaernarfon( neoPixelCount=NEO_PIXEL_COUNT )
        pixels2 = caernarfon.initNeoPixOnServo( 2, 23 )
        
        pixels = caernarfon.pixels
        
        circle8A =  pixels.nextNLights(8)
        stickB =    pixels2.nextNLights(8)
        stickB2 =   pixels2.nextNLights(8)
        
        act1 = main.addScene( "firstAct" )

        s = caernarfon.initServo( 1,"servo1" )
        
        p9 = main.adafruitFactory.addPCA9685(frequency=140)
        s2 = p9.addOutput(0,"s2")
        
        act1.addPatterns(
            Rainbow(circle8A),
            Rainbow(stickB2, colorCycle=0.7),
            Rainbow(stickB, colorCycle=0.7),
        )
        

        loopyCycle = 15.0
        @act1.addSimpleTaskDef( period=0.1 )
        def loopy(context=None):
            when = main.when
            v = (divmod(when,loopyCycle)[1]) / loopyCycle
            v = ((v - 0.5) * 1.3) + 0.5
            s.set( v, context )
            s2.set(v, context )
            
        act2 = main.addScene( "secondAct" )
        # act2.addRule( caernarfon.servo1, TERM(20) + (MILLIS / 100)%160 )
        
        sceneManager = main.scenes
        
        
        #####################################################################

                                    
 
        print(f"sources = {act1.sources()}" )

def demoMain(*args,**kwds):
    
    demo = CaernarfonTester( *args, **kwds )
    demo.run()