from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayBehaviorImport = getImportProfiler( globals() ) # "Behaviors.Behavior"

# pyright: reportUnusedImport=false

_sayBehaviorImport( "Expression" )
from LumensalisCP.Eval.Expressions import EvaluationContext, UpdateContext 

from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.Scenes.Scene import Scene
from LumensalisCP.Debug import Debuggable

if TYPE_CHECKING:
    #import weakref
    from LumensalisCP.Main.Manager import MainManager
    from LumensalisCP.Behaviors.Actor import Actor

_sayBehaviorImport( "parsing" )

class Behavior(Debuggable):
    __name: str
    __actor: weakref.ReferenceType[Actor] 
    __scene: str|Scene|None

    class KWDS(TypedDict):
        name:NotRequired[str]
        scene:NotRequired[str|Scene]
    
    def __init__(self, actor:Actor, name:Optional[str] = None, scene:Optional[str|Scene] = None ):
        super().__init__()
        self.__name = name or self.__class__.__name__
        self.__actor = weakref.ref(actor)
        self.__scene = scene
        
    @property
    def name(self) -> str:
        """Name of the behavior."""
        return self.__name  
    
    def setScene(self, scene:str|Scene|None):
        """ select a scene to be automatically activated when entering this behavior."""
        self.__scene = scene
        if scene is not None and self.isActive:
            context = UpdateContext.fetchCurrentContext(None)
            context.main.scenes.currentScene = scene

    def derivedEnter(self, context:EvaluationContext) -> None:
        pass

    def enter(self, context:EvaluationContext) -> None:
        """Enter the behavior. This is called when the behavior is activated."""
        if self.enableDbgOut: self.dbgOut("Entering behavior %s", self.name)
        if self.__scene is not None:
            context.main.scenes.currentScene = self.__scene
        self.derivedEnter(context)

    def derivedExit(self, context:EvaluationContext) -> None:
        pass

    def exit(self, context:EvaluationContext) -> None: # pylint: disable=unused-argument
        """Exit the behavior. This is called when the behavior is deactivated."""
        if self.enableDbgOut: self.dbgOut("Exiting behavior %s", self.name)    
        self.derivedExit(context)
        
    @property
    def actor(self) -> Actor:
        rv = self.__actor()   
        assert rv is not None
        return rv
        
    @property
    def isActive(self): return self.actor.currentBehavior is self
    
    def __bool__(self):
        """Return True if the behavior is active."""
        return self.actor.currentBehavior is self

_sayBehaviorImport.complete(globals())
