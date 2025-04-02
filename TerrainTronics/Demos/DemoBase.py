from LumensalisCP.Main.Manager import MainManager

from LumensalisCP.Main.Terms import *
from LumensalisCP.Main.Expressions import InputSource, OutputTarget, EvaluationContext
from LumensalisCP.Scenes.Scene import addSceneTask
from TerrainTronics.Caernarfon.Castle import onIRCode
from LumensalisCP.CPTyping  import *
from LumensalisCP.Triggers import Trigger, fireOnSet, fireOnTrue
import board, microcontroller

class DemoBase(object):
    pass
    def __init__(self, *args,**kwds):
        self.main = MainManager()
        
    def setup(self):
        pass
    
    def singleLoop(self):
        pass
    
    def run(self):
        print( "DemoBase setup" )
        self.setup()
        self.main.addTask( self.singleLoop )
        print( "DemoBase main.run() ..." )
        self.main.run()