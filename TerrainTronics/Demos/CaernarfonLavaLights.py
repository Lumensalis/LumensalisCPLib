from TerrainTronics.Demos.DemoBase import DemoBase
from random import randrange

class CaernarfonLavaLights( DemoBase ):
    
    softwareVersion = "V1.0"
    softwareDate = "12/2/21"
    CaernarfonVer = "1p0"
    
    NUMPIXELS = 64
    
    def __init__(self, *args, **kwds):
        super().__init__(*args,**kwds)
        self.ledState = 0
        
    def setup(self):
        self.caernarfon = self.main.addCaernarfon( neoPixelCount=self.NUMPIXELS )
        
        self.caernarfon.pixels.brightness = 1.0
        for i in range(self.NUMPIXELS-1):
            self.caernarfon.pixels[i] = (255,0,0) # This sets all pixels to red
        self.caernarfon.pixels.show()
        self.main.msDelay(1000)
        
        print("*****")
        self.main.msDelay(100)
        print(f'''TerrainTronics Collaboration with Tabletop Witchcraft
Version {self.softwareVersion} Date: {self.softwareDate} Caernarfon HW Version {self.CaernarfonVer}
''')
        
    def singleLoop(self):
        if self.ledState == 0:
            strip = self.caernarfon.pixels
            strip[0] = (255,255,255); # This is used to set up the outputs on the Caernarfon Neopixel device.
            for i in range(self.NUMPIXELS-1):
                j = randrange(0,63); #  32 in 64 chance that there will be a flicker that isn't pure red.
                if j < 32:
                    # //Colors are arrange Pixel, R, G, B.
                    strip[i] = (randrange(160,255),randrange(0,50),randrange(0,10)); # Tjese numbers are tuned to be inthe range of red to orange 
            strip.show()
            self.main.cyclesPerSecond = randrange(300,600) * 0.01

def demoMain(*args,**kwds):
    
    demo = CaernarfonLavaLights( *args, **kwds )
    demo.run()
    