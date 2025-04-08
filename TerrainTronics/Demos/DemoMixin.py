from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.CPTyping  import *
from LumensalisCP.common import *

class DemoMixin:
    # main: MainManager
    main: MainManager
    
    @property
    def TerrainTronics(self): return self.main.TerrainTronics
    
    @property
    def when(self) -> TimeInSeconds:
        return self.main.when 
    
    @property
    def currentScene(self): return self.main.scenes.currentScene