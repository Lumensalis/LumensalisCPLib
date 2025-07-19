from LumensalisCP.CPTyping import *
from LumensalisCP.Debug import Debuggable
from LumensalisCP.common import *
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Main.Dependents import MainRef
from LumensalisCP.Inputs import InputSource
from LumensalisCP.Main.Profiler import ProfileFrame, ProfileSubFrame, ProfileStubFrame

from LumensalisCP.Lights.Values import RGB
from LumensalisCP.Main.Manager import MainManager
import LumensalisCP.Main.Manager 
from  LumensalisCP.Main.Expressions import EvaluationContext
from LumensalisCP.Inputs import InputSource
type DirectValue = int|bool|float|RGB

import LumensalisCP.Main.Releasable

class UpdateContextDebugManager(LumensalisCP.Main.Releasable.Releasable):
    prior_debugEvaluate:bool
    prior_debugIndent:int
    context:EvaluationContext
    debugEvaluate:bool
    
    def __init__( self ): ...
    def prepare( self, context:'UpdateContext', debugEvaluate = True ): ...
    
    def __enter__(self) -> 'UpdateContextDebugManager': ...
        
    def __exit__(self, eT, eV, eTB ): ...

    def releaseNested(self): ...
    
    def say( self, message, *args, instance:Optional[Debuggable]=None ) -> None: ...
        
class UpdateContext(Debuggable):
    def __init__( self, main:MainManager ): pass
    
    main: MainManager
    when: TimeInSeconds 
    updateIndex: int
    changedSources: List[InputSource]
    activeFrame: ProfileFrame
    baseFrame: ProfileFrame
    debugEvaluate:bool
    _debugIndent:int
    

    def addChangedSource( self, changed:InputSource):pass
        
    def valueOf( self, value:Any ) -> Any: pass
    
    def subFrame(self, name:Optional[str]=None, name2:Optional[str]=None) -> ProfileSubFrame: pass
    def stubFrame(self, name:Optional[str]=None, name2:Optional[str]=None) -> ProfileStubFrame: pass

    @staticmethod
    def fetchCurrentContext( context:Optional[EvaluationContext]|None ) -> EvaluationContext: pass
    
    def nestDebugEvaluate(self, debugEvaluate:bool|None = None ) -> UpdateContextDebugManager: ...

    def reset( self, when:TimeInMS|None = None ): ...
            
OptionalContextArg = Optional[EvaluationContext]

#############################################################################

#Type 

class Evaluatable(Debuggable):
    enableDbgEvaluate : bool
    def getValue(self, context:Optional[EvaluationContext]=None) -> DirectValue: pass

def evaluate( value:Evaluatable|DirectValue, context:EvaluationContext|None = None ) -> DirectValue: pass

#############################################################################
            
class RefreshCycle(object):
    def __init__(self, refreshRate:TimeInSeconds = 0.1): pass

    def ready( self, context:EvaluationContext ) -> bool: pass

class Refreshable( object ):
    def __init__(self, refreshRate:TimeInSeconds = 0.1 ): pass
    
    @final
    def refresh( self, context:EvaluationContext): pass

#############################################################################