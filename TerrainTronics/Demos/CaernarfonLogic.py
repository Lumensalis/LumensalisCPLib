from TerrainTronics.Demos.DemoBase import DemoBase
from LumensalisCP.Main.Terms import *

class CaernarfonLogicDemo( DemoBase ):
    def setup(self):
        main = self.main
  
        #############################################################################
        # Add a CaernarfonCastle
        NEO_PIXEL_COUNT = 9
        self.caernarfon = caernarfon = main.addCaernarfon( neoPixelCount=NEO_PIXEL_COUNT, servos=1 )



        COLOR_CYCLE = 3.0
        NEO_PIXEL_SPREAD = 4
        pxStep = 1 / (NEO_PIXEL_COUNT *  NEO_PIXEL_SPREAD)

        def rainbow():
            A =  main.seconds / COLOR_CYCLE
            
            # set each pixel
            for px in range(NEO_PIXEL_COUNT):
                caernarfon.pixels[px] = main.wheel1( A + (px * pxStep) )
                
            caernarfon.pixels.show()


        lightLevel = caernarfon.A0.addAnalogInput( "lightLevel" )
        doorSwitch = caernarfon.D5.addInput( "doorSwitch" )
        plateSensor = caernarfon.D7.addInput( "plateSensor" )

        led_0 = caernarfon.D4.addOutput("led_0" )

        act1 = main.addScene( "firstAct" )

        act1.addRule(  led_0, 
                     doorSwitch & ~plateSensor
                ).when( 
                    lightLevel > 35
                ).otherwise(
                    plateSensor 
                )
            
        act1.addRule( caernarfon.servo1, TERM(20) + (MILLIS / 20)%160 )


        act1.addTask( rainbow, period=0.05 )

        
        print(f"sources = {act1.sources()}" )

def demoMain(*args,**kwds):
    
    demo = CaernarfonLogicDemo( *args, **kwds )
    demo.run()