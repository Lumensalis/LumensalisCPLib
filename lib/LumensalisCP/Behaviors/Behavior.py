from ..Main.Manager import MainManager
from ..Main.Expressions import EvaluationContext

from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.Main.Profiler import Profiler

class Actor(Debuggable):
    """
    Base class for actors in the scene.
    
    """
    
    __currentBehavior:"Behavior"|None = None
    
    def __init__(self, name:str|None = None, main:MainManager|None = None ):
        
        super().__init__()
        self.name = name if name else self.__class__.__name__
        self.main = main
        self.__currentBehavior = None
        
    @property
    def currentBehavior(self) -> "Behavior":
        """Current behavior of the actor."""
        return self.__currentBehavior

    @currentBehavior.setter
    def currentBehavior(self, behavior:"Behavior" ) -> None:
        """Set the current behavior of the actor."""
        self.setCurrentBehavior( behavior )
        
    def setCurrentBehavior(self, behavior:"Behavior", reset:bool=False ) -> None:
        """Set the current behavior of the actor."""
        if self.__currentBehavior is behavior and reset is False:   
            self.dbgOut("Behavior %s is already current, not changing", behavior.name)
            return
        
        self.dbgOut("Setting current behavior to %s", behavior.name)
        if self.__currentBehavior is not None:
            self.__currentBehavior.exit(self.main.context)
        self.__currentBehavior = behavior
        if self.__currentBehavior is not None:
            self.__currentBehavior.enter(self.main.context)
        
class Behavior(Debuggable):
    __name: str|None 
    __actor: weakref.WeakReference[Actor] 
    
    @property
    def name(self) -> str:
        """Name of the behavior."""
        return self.__name  
    
    def enter(self, context:EvaluationContext) -> None:
        """Enter the behavior. This is called when the behavior is activated."""
        self.dbgOut("Entering behavior %s", self.name)
    
    def exit(self, context:EvaluationContext) -> None:
        """Exit the behavior. This is called when the behavior is deactivated."""
        self.dbgOut("Exiting behavior %s", self.name)    
        
    @property
    def actor(self) -> Actor:
        return self.__actor()   
        
    def __init__(self, actor:Actor, name:str|None = None ):
        self.__name = name if name else self.__class__.__name__
        self.__actor = weakref.ref(actor)
        
    
    def __bool__(self):
        """Return True if the behavior is active."""
        return self.actor.currentBehavior is self