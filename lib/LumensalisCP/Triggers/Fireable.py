from LumensalisCP.Debug import Debuggable
from LumensalisCP.IOContext import *
from LumensalisCP.Main.Updates import evaluate
from LumensalisCP.util import kwCallback

if TYPE_CHECKING:
    FireableCBArg = Union[Callable,'Fireable',KWCallback]
    FireCondition = Union[bool,Callable,Evaluatable]

class Fireable( Debuggable ):

    @classmethod
    def makeCallback( cls, cb:FireableCBArg, *args, **kwds ):
        return FireableCB( cb, *args, **kwds )
        
    @classmethod
    def makeDbgCallback( cls, cb:FireableCBArg, *args, **kwds ):
        rv = FireableCB( cb, *args, **kwds )
        rv.enableDbgOut = True
        return rv

    def __init__(self):
        super().__init__()
    
    def fire(self, context:EvaluationContext) -> Any:
        raise NotImplemented
    
    def unless( self, condition:FireCondition):
        return FireableUnless( condition, self )
    
    def __call__(self, context:Optional[EvaluationContext]=None) ->Any :
        return self.fire(context=EvaluationContext.fetchCurrentContext(context))
        

class FireableCB( Fireable ):

    def __init__( self, cb:FireableCBArg, *args, **kwds ):
        super().__init__()
        self._args = args
        self._kwds = kwds
        self._cb = KWCallback( cb )
    
    def fire(self, context:EvaluationContext) ->Any :
        
        if self.enableDbgOut or context.debugEvaluate: 
            with context.nestDebugEvaluate() as nde:
                nde.say( self, "firing" )
                rv = self._cb( *self._args, context=context,**self._kwds )
                return rv
        else:
            return self._cb( *self._args, context=context,**self._kwds )
    
class FireableUnless( Fireable ):

    def __init__( self, condition:FireCondition, action:Fireable ):
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
        