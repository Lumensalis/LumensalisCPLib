from __future__ import annotations


from LumensalisCP.ImportProfiler import  getImportProfiler
_sayBehaviorImport = getImportProfiler( globals() ) # "Behaviors.Behavior"


_sayBehaviorImport( "Expression" )
from LumensalisCP.Eval.Expressions import EvaluationContext, UpdateContext 

from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.Scenes.Scene import Scene
from LumensalisCP.Debug import Debuggable

if TYPE_CHECKING:
    #import weakref
    from LumensalisCP.Main.Manager import MainManager

_sayBehaviorImport( "parsing" )
class Actor(Debuggable):
    """
    Base class for actors in the scene.
    
    """
    
    __currentBehavior:Behavior|None = None
    class KWDS(TypedDict):
        name: NotRequired[str]
        main: NotRequired[MainManager]
        
    def __init__(self, name:str|None = None, main:MainManager|None = None ):
        
        super().__init__()
        self.name = name if name else self.__class__.__name__
        main = main or getMainManager()
        assert main is not None
        self.main = main 
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
        
        if self.enableDbgOut: self.dbgOut("Setting current behavior to %s", behavior.name)
        context = UpdateContext.fetchCurrentContext(context)
        if self.__currentBehavior is not None:
            self.__currentBehavior.exit(context)
        self.__currentBehavior = behavior
        if self.__currentBehavior is not None: # pylint: disable=protected-access # pyright: ignore[reportUnnecessaryComparison]
            self.__currentBehavior.enter(context)
        
class Behavior(Debuggable):
    __name: str
    __actor: weakref.ReferenceType[Actor] 
    __scene: str|Scene|None
    
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
        
    def enter(self, context:EvaluationContext) -> None:
        """Enter the behavior. This is called when the behavior is activated."""
        if self.enableDbgOut: self.dbgOut("Entering behavior %s", self.name)
        if self.__scene is not None:
            context.main.scenes.currentScene = self.__scene
    
    def exit(self, context:EvaluationContext) -> None: # pylint: disable=unused-argument
        """Exit the behavior. This is called when the behavior is deactivated."""
        if self.enableDbgOut: self.dbgOut("Exiting behavior %s", self.name)    
        
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
