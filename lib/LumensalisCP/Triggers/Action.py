from __future__ import annotations

from LumensalisCP.Main.PreMainConfig import ImportProfiler
_sayActionImport = ImportProfiler( "Action" )

from LumensalisCP.Debug import Debuggable

_sayActionImport( "IOContext" )
from LumensalisCP.IOContext import *

_sayActionImport( "Behavior" )
from LumensalisCP.Behaviors.Behavior import Behavior, Actor  # type: ignore[import-untyped]

if TYPE_CHECKING:
    #from LumensalisCP.util import kwCallback

    ActionCBArg:TypeAlias = Union[Callable[...,Any],'Action',KWCallback]
    FireCondition:TypeAlias = Union[bool,Callable[...,bool],Evaluatable[bool]]

_sayActionImport( "parsing..." )

ActionDoArg:TypeAlias = Union[Callable[...,Any],KWCallback,Behavior,'Action']

class Action( Debuggable ):
    """ Base class for Actions 
    """


    @classmethod
    def makeAction( cls, what:ActionDoArg, *args:Any, **kwds:StrAnyDict ) ->Action:
        if isinstance(what, Action):
            assert not args and not kwds, "Action.makeAction called with Action and additional arguments"
            return what
        if isinstance(what, Behavior):
            assert not args and not kwds, "Action.makeAction called with Behavior and additional arguments"
            return ActionSelectBehavior(what)

        return ActionCB( what, *args, **kwds )
        

    @classmethod
    def makeCallback( cls, cb:ActionCBArg, *args:Any, **kwds:StrAnyDict ) -> ActionCB:
        return ActionCB( cb, *args, **kwds )
        
    @classmethod
    def makeDbgCallback( cls, cb:ActionCBArg, *args:Any, **kwds:StrAnyDict ) -> ActionCB:
        rv = ActionCB( cb, *args, **kwds )
        rv.enableDbgOut = True
        return rv

    def __init__(self):
        super().__init__()
    
    def fire(self, context:EvaluationContext) -> Any:
        """ "do" the action """
        raise NotImplementedError
    
    def unless( self, condition:FireCondition) -> ActionUnless:
        """ add a condition to the action, if the condition is true, the action will not be fired. """
        return ActionUnless( condition, self )
    
    def __call__(self, context:Optional[EvaluationContext]=None) ->Any :
        """ invokes the action"""
        return self.fire(context=UpdateContext.fetchCurrentContext(context))

class ActionSelectBehavior( Action ):
    """ Action which starts a behavior."""

    def __init__( self, behavior:Behavior) -> None:
        self.behavior = behavior
    
    def fire(self, context:EvaluationContext) ->Any :
        if self.enableDbgOut or context.debugEvaluate: 
            with context.nestDebugEvaluate() as nde:
                nde.say( self, "activating behavior %s", self.behavior.name )
                return self.behavior.actor.setCurrentBehavior(self.behavior, context=context)
        else:
            return self.behavior.actor.setCurrentBehavior(self.behavior, context=context)


class ActionCB( Action ):
    """ Action which calls a callback function with the given arguments."""

    def __init__( self, cb:ActionCBArg, *args:Any, **kwds:StrAnyDict  ) -> None:
        super().__init__()
        self._args = args
        self._kwds = kwds
        self._cb = KWCallback( cb )
    
    def fire(self, context:EvaluationContext) ->Any :
        
        if self.enableDbgOut or context.debugEvaluate: 
            with context.nestDebugEvaluate() as nde:
                nde.say( self, "firing" )
                rv = self._cb( *self._args, context=context,**self._kwds ) # type: ignore
                return rv
        else:
            return self._cb( *self._args, context=context,**self._kwds ) # type: ignore
    
class ActionUnless( Action ):

    def __init__( self, condition:FireCondition, action:Action ) -> None:
        super().__init__()
        self._condition = condition
        self._action =  action
        self.enableDbgOut = action.enableDbgOut
        
    def fire(self, context:EvaluationContext) ->Any :
        if self.enableDbgOut or context.debugEvaluate: 
            with context.nestDebugEvaluate() as nde:
                
                unless = evaluate(self._condition,context )  # type: ignore
                if not unless:
                    nde.say( self, "unless firing..." )
                    return self._action.fire( context )
                else:
                    nde.say( self, "unless skipped" )
                    
        else:
            unless = evaluate(self._condition,context ) # type: ignore
            if not unless:
                return self._action.fire( context )

_sayActionImport( "complete." )
