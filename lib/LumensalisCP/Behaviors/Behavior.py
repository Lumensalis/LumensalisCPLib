from __future__ import annotations
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Main.Expressions import EvaluationContext 

from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.Main.Profiler import Profiler
from LumensalisCP.Scenes.Scene import Scene
from LumensalisCP.Debug import Debuggable

if TYPE_CHECKING:
    import weakref

class Actor(Debuggable):
    """
    Base class for actors in the scene.
    
    """
    
    __currentBehavior:Behavior|None = None
    
    def __init__(self, name:str|None = None, main:MainManager|None = None, **kwds ):
        
        super().__init__(**kwds)
        self.name = name if name else self.__class__.__name__
        main = main or MainManager.theManager
        assert main is not None
        self.main = main 
        self.__currentBehavior = None
        
    @property
    def currentBehavior(self) -> "Behavior|None":
        """Current behavior of the actor."""
        #assert self.__currentBehavior is not None
        return self.__currentBehavior

    @currentBehavior.setter
    def currentBehavior(self, behavior:"Behavior" ) -> None:
        """Set the current behavior of the actor."""
        self.setCurrentBehavior( behavior )
        
    def setCurrentBehavior(self, behavior:"Behavior", reset:bool=False ) -> None:
        """Set the current behavior of the actor."""
        if self.__currentBehavior is behavior and reset is False:   
            if self.enableDbgOut: self.dbgOut("Behavior %s is already current, not changing", behavior.name)
            return
        
        if self.enableDbgOut: self.dbgOut("Setting current behavior to %s", behavior.name)
        if self.__currentBehavior is not None:
            self.__currentBehavior.exit(self.main.getContext())
        self.__currentBehavior = behavior
        if self.__currentBehavior is not None:
            self.__currentBehavior.enter(self.main.getContext())
        
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
        self.__scene = scene
        if scene is not None and self.isActive:
            context = EvaluationContext.fetchCurrentContext(None)
            context.main.scenes.currentScene = scene
        
    def enter(self, context:EvaluationContext) -> None:
        """Enter the behavior. This is called when the behavior is activated."""
        if self.enableDbgOut: self.dbgOut("Entering behavior %s", self.name)
        if self.__scene is not None:
            context.main.scenes.currentScene = self.__scene
    
    def exit(self, context:EvaluationContext) -> None:
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