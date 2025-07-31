from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayActionImport = getImportProfiler( globals() ) # "Action"

from LumensalisCP.Debug import Debuggable

_sayActionImport( "IOContext" )
from LumensalisCP.IOContext import *


_sayActionImport( "Behavior" )
from LumensalisCP.Behaviors.Behavior import Behavior, Actor  # type: ignore[import-untyped]

from LumensalisCP.Triggers.Invocable import Invocable

#if TYPE_CHECKING:
    #from LumensalisCP.util import kwCallback

_sayActionImport( "parsing..." )

#if TYPE_CHECKING:
#    FireCondition:TypeAlias = Union[bool,Callable[...,bool],Evaluatable[bool]]
#else:
FireCondition:TypeAlias = Union[bool,Callable[...,bool],'Evaluatable[bool]']

ActionDoArg:TypeAlias = Union[Callable[...,Any],KWCallback,Behavior,'Action']
#ActionCBArg:TypeAlias = Union[Callable[...,Any],'Action',KWCallback]
ActionCBArg:TypeAlias = Union[Callable[...,Any],'Action']

class Action( Debuggable, Invocable ):
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
        if len(args) > 0 or len(kwds) > 0:
            return ActionCBWithArgsAndKwds( what, *args, **kwds )
        elif isinstance(what, Invocable):
            return ActionCB( what )
        elif callable(what):
            return ActionCB( what )
        raise TypeError(f"Cannot convert {type(what)} to Action")

        
    @classmethod
    def makeDbgCallback( cls, cb:ActionCBArg, *args:Any, **kwds:StrAnyDict ) -> ActionCB:
        rv = ActionCB( cb, *args, **kwds )
        rv.enableDbgOut = True
        return rv

    def __init__(self):
        super().__init__()
    
    def fire(self, context:EvaluationContext) -> None:
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
    
    def fire(self, context:EvaluationContext) ->None :
        if self.enableDbgOut or context.debugEvaluate: 
            with context.nestDebugEvaluate() as nde:
                nde.say( self, "activating behavior %s", self.behavior.name )
                self.behavior.actor.setCurrentBehavior(self.behavior, context=context)
        else:
            self.behavior.actor.setCurrentBehavior(self.behavior, context=context)


class ActionCB( Action ):
    """ Action which calls a callback function with the given arguments."""

    def __init__( self, cb:ActionCBArg ) -> None:
        super().__init__()
        self._cb = cb # KWCallback( cb )
        self.name:str = getattr(cb, '__name__', repr(cb) )

    def __repr__(self) -> str:
        return f"({self.__class__.__name__}@ {hex(id(self))} {self.name!r} )" 

    def __invoke(self, context:EvaluationContext) -> Any:
        self.dbgOut( f"in __invoke" )
        try:
            if self.enableDbgOut: self.dbgOut( f"invoking _cb {self._cb!r}" )
            rv =  self._cb( context )
            if self.enableDbgOut: self.dbgOut( "rv = %s ", rv )
        except Exception as inst:
            self.SHOW_EXCEPTION( inst, "invoking action %s", self.name )
            raise   

    def fire(self, context:EvaluationContext) -> None :
        
        if self.enableDbgOut or context.debugEvaluate: 
            with context.nestDebugEvaluate() as nde:
                nde.say( self, " firing... " )
                return self.__invoke(context)
        else:
            return self.__invoke(context)
        
    def __call__(self, 
                inputOrContext:Optional[EvaluationContext|InputSource]=None,
                context:Optional[EvaluationContext]=None
            ) ->Any :
        if context is None:
            if isinstance(inputOrContext, EvaluationContext):
                context = inputOrContext
            else:
                context = UpdateContext.fetchCurrentContext(None)
            context=UpdateContext.fetchCurrentContext(context)
        return self.__invoke(context)



class ActionCBWithArgsAndKwds( Action ):
    """ Action which calls a callback function with the given arguments."""

    def __init__( self, cb:ActionCBArg, *args:Any, **kwds:StrAnyDict  ) -> None:
        super().__init__()
        self._args = args
        self._kwds = kwds
        self._cb = cb # KWCallback( cb )
        self.name:str = getattr(cb, '__name__', repr(cb) )

    def __repr__(self) -> str:
        return f"({self.__class__.__name__}@ {hex(id(self))} {self.name!r} cb={self._cb!r} )" 

    def __invoke(self, context:EvaluationContext) -> Any:
        self.dbgOut( f"in __invoke" )
        try:
            return  self._cb( *self._args, context=context,**self._kwds ) # type: ignore
        except Exception as inst:
            self.SHOW_EXCEPTION( inst, "invoking action %s with args=%r, kwds=%r", self.name, self._args, self._kwds )
            raise   

    def fire(self, context:EvaluationContext) -> None :
        
        if self.enableDbgOut or context.debugEvaluate: 
            with context.nestDebugEvaluate() as nde:
                nde.say( self, " firing... " )
                return self.__invoke(context)
        else:
            return self.__invoke(context)
        
    def __call__(self, inputOrContext:Optional[EvaluationContext|InputSource]=None, context:Optional[EvaluationContext]=None) ->Any :
        if context is None:
            if isinstance(inputOrContext, EvaluationContext):
                context = inputOrContext
            else:
                context = UpdateContext.fetchCurrentContext(None)
            context=UpdateContext.fetchCurrentContext(context)
        return self.__invoke(context)

class ActionUnless( Action ):

    def __init__( self, condition:FireCondition, action:Action ) -> None:
        super().__init__()
        self._condition = condition
        self._action =  action
        self.enableDbgOut = action.enableDbgOut
        
    def fire(self, context:EvaluationContext) ->None :
        if self.enableDbgOut or context.debugEvaluate: 
            with context.nestDebugEvaluate() as nde:
                
                unless = evaluate(self._condition,context )  # type: ignore
                if not unless:
                    nde.say( self, "unless firing..." )
                    self._action.fire( context )
                    return 
                else:
                    nde.say( self, "unless skipped" )
                    
        else:
            unless = evaluate(self._condition,context ) # type: ignore
            if not unless:
                self._action.fire( context )


DoArg:TypeAlias = Union[Callable[...,Any],KWCallback,Behavior]

def do( cb:DoArg, *args:Any, **kwds:StrAnyDict ) -> Action:
    """ create an Action : see see http://lumensalis.com/ql/h2Actions"""
    return Action.makeAction( cb, *args, **kwds )

def doDbg( cb:DoArg, *args:Any, **kwds:StrAnyDict ) -> Action:
    rv = Action.makeAction( cb, *args, **kwds )
    rv.enableDbgOut = True
    return rv

__all__ = [
    'Action',
    'ActionCBWithArgsAndKwds',
    'ActionUnless',
    'do',
    'doDbg',
    'ActionCB',
    'ActionSelectBehavior',
    'ActionDoArg',
    'ActionCBArg',
]

_sayActionImport.complete(globals())
