from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Main.Terms import *
from LumensalisCP.CPTyping  import *
from LumensalisCP.common import *

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
        
class DemoSubBase(object):
    pass
    def __init__(self, demo:DemoBase, *args,**kwds):
        self.demo = demo
        self.main = demo.main
        ensure( self.main.scenes.currentScene is not None, "You must have a scene defined before creating a %s", self.__class__.__name__)
        
    def setup(self):
        pass
    
