from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__sayImport = getImportProfiler( __name__, globals() )


# pylint: disable=unused-import
# pyright: reportUnusedImport=false

from LumensalisCP.common import *

#from LumensalisCP.Triggers.Invocable import *
from LumensalisCP.Triggers.Trigger import Trigger
from LumensalisCP.Eval.ExpressionTerm import rising, ExpressionTerm

if TYPE_CHECKING:
    from LumensalisCP.Triggers.Action import Action, ActionDoArg, ActionCB, ActionCBArg, ActionSelectBehavior
    from LumensalisCP.IOContext  import *
    from LumensalisCP.Eval.Expressions import Expression

#############################################################################
__sayImport.parsing()
def fireOnTrue( expression:Expression|ExpressionTerm, 
               target:ActionDoArg, 
               trigger:Optional[Trigger]=None
    ) -> Trigger :
    # assert trigger is not None
    #$def on2( cb:ActionDoArg, 
    #        expression:Expression|ExpressionTerm=expression, 
    #        trigger:Trigger|None=trigger 
    #    ) -> Trigger:
    cb = target
    name:str
    if trigger is None:
        try:
            assert isinstance(cb.__name__, str), f"cb.__name__ must be a string, got {type(cb.__name__)}" # type: ignore[reportCallIssue]
            name = cb.__name__ # type: ignore[reportCallIssue]
        except (AttributeError, AssertionError):
            name = repr(cb)
        trigger = Trigger( name=name )
    cTrigger = trigger 

    cTrigger.addAction( cb )
    cTrigger.fireOnTrue( expression )
    #print( f"wrapped for {callable.__name__} = {wrapped}, class={wrapped.__class__}")
    return cTrigger

#############################################################################

def fireOnTrueDef( expression:Expression|ExpressionTerm, 
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
                assert isinstance(cb.__name__, str), f"cb.__name__ must be a string, got {type(cb.__name__)}" # type: ignore[reportCallIssue]
                name = cb.__name__ # type: ignore[reportCallIssue]
            except (AttributeError, AssertionError):
                name = repr(cb)
            trigger = Trigger( name=name )
        cTrigger = trigger 

        cTrigger.addAction( cb )
        cTrigger.fireOnTrue( expression )
        #print( f"wrapped for {callable.__name__} = {wrapped}, class={wrapped.__class__}")
        return cTrigger
    
    if target is not None:
        return on2( target, expression=expression, trigger=trigger )
    return on2

#############################################################################

def fireOnRising( expression:ExpressionTerm, target:Any, trigger:Optional[Trigger]=None ) -> Trigger:
    return fireOnTrue( expression= rising( expression ), trigger=trigger, target=target )

def fireOnFalling( expression:ExpressionTerm, target:Action, trigger:Optional[Trigger]=None ) -> Trigger:
    return fireOnTrue( expression= falling( expression ), trigger=trigger, target=target )

#############################################################################
__all__ = [
    'fireOnTrue',
    'fireOnTrueDef',
    'fireOnRising',
    'fireOnFalling',
]

__sayImport.complete()
