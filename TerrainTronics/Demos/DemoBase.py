from LumensalisCP.Main import MainManager


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