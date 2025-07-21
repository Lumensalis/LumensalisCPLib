from __future__ import annotations

import LumensalisCP.Main.Manager 
from LumensalisCP.CPTyping import *
from LumensalisCP.Debug import Debuggable
from LumensalisCP.common import *
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Main.Dependents import MainRef
from LumensalisCP.Inputs import InputSource
from LumensalisCP.Main.Profiler import ProfileFrame, ProfileFrameBase, ProfileSubFrame, ProfileStubFrame
from LumensalisCP.util.Releasable import Releasable
from LumensalisCP.Lights.Values import RGB
from LumensalisCP.Eval.Expressions import EvaluationContext
type DirectValue = int|bool|float|RGB
    

# pylint: disable=unused-argument,super-init-not-called
class UpdateContextDebugManager(Releasable):
    prior_debugEvaluate:bool
    prior_debugIndent:int
    context:EvaluationContext
    debugEvaluate:bool
    
    def __init__( self ) -> None: ...
    def prepare( self, context:'UpdateContext', debugEvaluate:bool = True ) -> None: ...
    
    def __enter__(self) -> Self: ...
        
    def __exit__(self, eT:Type[BaseException], eV:BaseException, eTB:Any) -> None: ...

    def releaseNested(self): ...
    
    def say( self, instanceOrMessage:Debuggable|str, *args:Any ) -> None:...
        
class UpdateContext(Debuggable):
    def __init__( self, main:MainManager ) -> None: ...
    
    main: MainManager
    when: TimeInSeconds 
    updateIndex: int
    #changedSources: List[InputSource]
    activeFrame: ProfileFrameBase
    baseFrame: ProfileFrameBase
    debugEvaluate:bool
    _debugIndent:int
    
    def addChangedSource( self, changed:InputSource) -> None: ...
    
    def subFrame(self, name:Optional[str]=None, name2:Optional[str]=None) -> ProfileSubFrame: ...
    def stubFrame(self, name:Optional[str]=None, name2:Optional[str]=None) -> ProfileStubFrame: ...
    def valueOf( self, value:Any ) -> Any: ...

    @staticmethod
    def fetchCurrentContext( context:Optional[EvaluationContext]|None ) -> EvaluationContext: ...
    
    def nestDebugEvaluate(self, debugEvaluate:Optional[bool] = None ) -> UpdateContextDebugManager: ...

    def reset( self, when:Optional[TimeInSeconds] = None ) -> None: ...
            
OptionalContextArg:TypeAlias = Optional[EvaluationContext]

#############################################################################



#############################################################################
