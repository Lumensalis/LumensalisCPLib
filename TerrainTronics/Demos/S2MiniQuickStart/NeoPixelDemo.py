#from TerrainTronics.Demos.DemoBase import DemoBase
from LumensalisCP.Main.Manager import MainManager

main = MainManager()

# how many NeoPixels are in your chain?
NEO_PIXEL_COUNT = 9

caernarfon = main.addCaernarfon( neoPixelCount=NEO_PIXEL_COUNT )

priorSeconds = 0

def singleRainbowWheel():
    """
    
main.seconds gives the number of seconds since the controller started. This can be very useful when you want things to change over time
    
main.wheel1( A ) returns a gradually changing color which circles back  around from 0.0 to 1.0
    
so if we want to cycle through the colors every COLOR_CYCLE seconds, then
    
    A = main.seconds / COLOR_CYCLE
    
and if we want to spread 1/NEO_PIXEL_SPREAD of the available colors over our neo pixel chain, we need to offset

    1 / (NEO_PIXEL_COUNT *  NEO_PIXEL_SPREAD)

between pixels
"""
    
    COLOR_CYCLE = 3.0
    NEO_PIXEL_SPREAD = 4

    pxStep = 1 / (NEO_PIXEL_COUNT *  NEO_PIXEL_SPREAD)
    A =  main.seconds / COLOR_CYCLE
    
    # set each pixel
    for px in range(NEO_PIXEL_COUNT):
        caernarfon.pixels[px] = main.wheel1( A + (px * pxStep) )
        
    caernarfon.pixels.show()


def singleLoop():
    singleRainbowWheel()
    global priorSeconds
    if main.seconds - priorSeconds > 5:
        priorSeconds = main.seconds
        print( f"elapsedSeconds={main.seconds}")


def demoMain():
    main.addTask( singleLoop )
    main.run()

