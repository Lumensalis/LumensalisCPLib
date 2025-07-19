from LumensalisCP.Demo.DemoCommon import *
from LumensalisCP.Lights.Patterns import *

class TestLeds(DemoSubBase):
    pass
    def setup(self):

        scene = self.main.scenes.currentScene
        harlechXL = self.main.TerrainTronics.addHarlechXL()
        
        bankA = harlechXL.nextNLights(8)
        bankB = harlechXL.nextNLights(8)
        bankC = harlechXL.nextNLights(8)
        bankD = harlechXL.nextNLights(8)
        
                
        scene.addPatterns(
                        Blink( bankA, onValue=0.1 ),
                          Cylon(bankB),
                          Random(bankC,duration=0.2),
                          Blink(bankD),
                          )
        
        harlechXL.checkOpenShort()
