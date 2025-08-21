from __future__ import annotations


from LumensalisCP.ImportProfiler import  getImportProfiler
_sayBehaviorImport = getImportProfiler( globals() ) # "Behaviors.Behavior"

# pyright: reportUnusedImport=false

from LumensalisCP.Eval.Expressions import EvaluationContext, UpdateContext 

from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.Scenes.Scene import Scene
from LumensalisCP.Debug import Debuggable
from LumensalisCP.Temporal.Refreshable import RefreshableNAP

if TYPE_CHECKING:
    #import weakref
    from LumensalisCP.Main.Manager import MainManager
    from LumensalisCP.Behaviors.Behavior import Behavior
    
_sayBehaviorImport( "parsing" )
class Actor(RefreshableNAP):
    """
    Base class for actors in the scene.
    
    """
    
    __currentBehavior:Behavior|None = None
    class KWDS(RefreshableNAP.KWDS):
        #name: NotRequired[str]
        main: NotRequired[MainManager]
        
    def __init__(self,  main:MainManager|None = None,**kwds:Unpack[RefreshableNAP.KWDS] ):
        
        main = main or getMainManager()
        assert main is not None
        self.main = main 
        kwds.setdefault('autoList',main._refreshables ) # type: ignore[assignment]
        kwds.setdefault('temporaryName', self.__class__.__name__ )
        super().__init__(**kwds)
        self.__currentBehavior = None
        
    @property
    def currentBehavior(self) -> Behavior|None:
        """Current behavior of the actor."""
        #assert self.__currentBehavior is not None
        return self.__currentBehavior

    @currentBehavior.setter
    def currentBehavior(self, behavior:Behavior ) -> None:
        """Set the current behavior of the actor."""
        self.setCurrentBehavior( behavior )
        
    def setCurrentBehavior(self, behavior:Behavior|None, reset:bool=False, context:Optional[EvaluationContext]=None ) -> None:
        """Set the current behavior of the actor."""
        assert behavior is not None, "Behavior must not be None"
        if self.__currentBehavior is behavior and reset is False:   
            if self.enableDbgOut: self.dbgOut("Behavior %s is already current, not changing", behavior.name)
            return
        
        if self.enableDbgOut: self.dbgOut("Setting current behavior to %s (%s)", behavior.name, behavior.__class__.__name__)
        context = UpdateContext.fetchCurrentContext(context)
        if self.__currentBehavior is not None:
            self.__currentBehavior.exit(context)
        self.__currentBehavior = behavior
        if self.__currentBehavior is not None: # pylint: disable=protected-access # pyright: ignore[reportUnnecessaryComparison]
            self.__currentBehavior.enter(context)
        
_sayBehaviorImport.complete(globals())
