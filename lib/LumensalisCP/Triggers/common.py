from __future__ import annotations

#from LumensalisCP.CPTyping import *
#from LumensalisCP.common import Debuggable
#from LumensalisCP.Inputs import InputSource
from LumensalisCP.Main.PreMainConfig import ImportProfiler
__triggersCommonSayImport = ImportProfiler("Triggers.common" )

__triggersCommonSayImport( "IOContext... " )
from LumensalisCP.IOContext  import *

__triggersCommonSayImport( "Trigger... " )
from LumensalisCP.Triggers.Trigger import Trigger

__triggersCommonSayImport( "Action... " )
from LumensalisCP.Triggers.Action import Action, ActionDoArg


#############################################################################


#############################################################################


def fireOnSet( source:Optional[InputSource]=None, trigger:Optional[Trigger]=None ): #type: ignore
    assert source is not None
    # assert trigger is not None
    def on2( cb:Callable[..., Any] ) -> Callable[..., Any]:
        cTrigger = trigger or Trigger( name=cb.__name__ )
        #callable._trigger = cTrigger
        cTrigger.fireOnSet( source )
        cTrigger.addAction( cb  )
        return cb
    return on2



def fireOnTrue( expression:Expression|ExpressionTerm, 
               target:Optional[ActionDoArg], 
               trigger:Optional[Trigger]=None
    ) -> Trigger | Callable[..., Trigger]:
    # assert trigger is not None
    def on2( cb:ActionDoArg, 
            expression:Expression|ExpressionTerm=expression, 
            trigger:Trigger|None=trigger 
        ) -> Trigger:

        name:str
        if trigger is None:
            try:
                assert isinstance(cb.__name__, str), f"cb.__name__ must be a string, got {type(cb.__name__)}"
                name = cb.__name__
            except (AttributeError, AssertionError):
                name = repr(cb)
            trigger = Trigger( name=name )
        cTrigger = trigger 
        # @functools.wraps(callable)
        #if len(args) == 0 and len(kwargs) == 0:
        #    def wrapped() -> Any:
        #        return cb()
        #    elif len(kwargs) == 0:
        def wrapped(*args:Any,**kwargs:StrAnyDict) -> Any:
            result = cb(*args, **kwargs)
            return result 
        
        try: setattr(cb, 'trigger', cTrigger )
        except: pass # pylint: disable=bare-except
        try: setattr(cb,'expression', expression )
        except: pass # pylint: disable=bare-except
        setattr(wrapped, 'trigger', cTrigger )
        setattr(wrapped,'expression', expression )
        #setattr( wrapped, '__name__', callable.__name__ )
        
        cTrigger.addAction( wrapped )
        cTrigger.fireOnTrue( expression )
        #print( f"wrapped for {callable.__name__} = {wrapped}, class={wrapped.__class__}")
        return cTrigger
    if target is not None:
        return on2( target, expression=expression, trigger=trigger )
    return on2

def fireOnClick( expression:Expression|ExpressionTerm, trigger:Optional[Trigger]=None ) -> Any:
    return fireOnTrue( expression=expression, trigger=trigger, target=None )

def fireOnRising( expression:ExpressionTerm, target:Any, trigger:Optional[Trigger]=None ) -> Any:
    return fireOnTrue( expression= rising( expression ), trigger=trigger, target=target )

def fireOnFalling( expression:ExpressionTerm, target:Action, trigger:Optional[Trigger]=None ) -> Any:
    return fireOnTrue( expression= falling( expression ), trigger=trigger, target=target )

__triggersCommonSayImport( "complete." )