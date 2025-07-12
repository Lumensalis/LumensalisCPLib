from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Main.Dependents import MainRef
from LumensalisCP.Inputs import InputSource
from LumensalisCP.Main.Profiler import ProfileFrame, ProfileSubFrame, ProfileStubFrame

from LumensalisCP.Lights.Values import RGB

type DirectValue = int|bool|float|RGB

class UpdateContext(object):
    def __init__( self, main:MainManager ): pass
    
    main: MainManager
    when: TimeInSeconds 
    updateIndex: int
    changedSources: List[InputSource]
    activeFrame: ProfileFrame
    baseFrame: ProfileFrame

    def addChangedSource( self, changed:InputSource):pass
        
    def valueOf( self, value:Any ) -> Any: pass
    
    def subFrame(self, name:Optional[str]=None, name2:Optional[str]=None) -> ProfileSubFrame: pass
    def stubFrame(self, name:Optional[str]=None, name2:Optional[str]=None) -> ProfileStubFrame: pass

    @staticmethod
    def fetchCurrentContext( context:"UpdateContext"|None ) -> "UpdateContext": pass
        
OptionalContextArg = Optional[UpdateContext]

#############################################################################

#Type 

class Evaluatable(object):
    
    def getValue(self, context:UpdateContext) -> DirectValue: pass

def evaluate( value:Evaluatable|DirectValue, context:UpdateContext|None = None ) -> DirectValue: pass

#############################################################################
            
class RefreshCycle(object):
    def __init__(self, refreshRate:TimeInSeconds = 0.1): pass

    def ready( self, context:UpdateContext ) -> bool: pass

class Refreshable( object ):
    def __init__(self, refreshRate:TimeInSeconds = 0.1 ): pass
    
    @final
    def refresh( self, context:UpdateContext): pass

#############################################################################