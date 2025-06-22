from LumensalisCP.CPTyping import *
from LumensalisCP.common import *

from LumensalisCP.Main.Dependents import MainRef
#import LumensalisCP.Main.Expressions as Expressions
import LumensalisCP.Main
from LumensalisCP.Main.Profiler import ProfileFrame, ProfileSubFrame

class UpdateContext(object):
    pFrame: ProfileFrame
    
    def __init__( self, main:"LumensalisCP.Main.Manager.MainManager"=None ):
        self.__updateIndex = 0
        self.__changedSources : List["LumensalisCP.Main.Expressions.InputSource"] = []
        self.__mainRef = main.makeRef()
        self.__when = main.when
        self.pFrame = None
        
    def reset( self ):
        self.__updateIndex += 1
        self.__changedSources = []
        self.__when = self.main.when
        self.pFrame = None
        
    @property
    def main(self): return self.__mainRef()
        
    @property
    def when(self) -> TimeInSeconds : return self.__when
    
    @property
    def updateIndex(self): return self.__updateIndex

    @property
    def changedSources(self): return self.__changedSources
    
    def subFrame(self, name:str|None=None) -> ProfileSubFrame:
        rv = self.pFrame.activeFrame().subFrame(self, name)
        assert rv
        return rv

    def addChangedSource( self, changed:"LumensalisCP.Main.Expressions.InputSource"):
        self.__changedSources.append( changed )
        
    def valueOf( self, value:Any ) -> Any:
        raise NotImplemented


class RefreshCycle(object):
    def __init__(self, refreshRate:TimeInSeconds = 0.1):
        self.refreshRate = refreshRate
        self.nextRefresh = 0
        
    def ready( self, context:UpdateContext ):
        if self.nextRefresh >= context.when: return False
        
        self.nextRefresh = context.when + self.refreshRate
        return True

class Refreshable( object ):
    def __init__(self, refreshRate:TimeInSeconds = 0.1 ):
        self.__refreshCycle = RefreshCycle( refreshRate=refreshRate )
    
    @final
    def refresh( self, context:UpdateContext):
        if self.__refreshCycle.ready(context):
            self.doRefresh(context)

#############################################################################