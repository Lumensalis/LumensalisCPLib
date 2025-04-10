from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Main.Dependents import MainRef
from LumensalisCP.Main.Expressions import InputSource

class UpdateContext(object):
    def __init__( self, main:MainManager ): pass
    
    main: MainManager
    when: TimeInSeconds 
    updateIndex: int
    changedSources: List[InputSource]

    def addChangedSource( self, changed:InputSource):pass
        
    def valueOf( self, value:Any ) -> Any: pass
        
class RefreshCycle(object):
    def __init__(self, refreshRate:TimeInSeconds = 0.1): pass

    def ready( self, context:UpdateContext ) -> bool: pass

class Refreshable( object ):
    def __init__(self, refreshRate:TimeInSeconds = 0.1 ): pass
    
    @final
    def refresh( self, context:UpdateContext): pass

#############################################################################