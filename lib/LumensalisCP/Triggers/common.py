from __future__ import annotations

# pylint: disable=unused-import
# pyright: reportUnusedImport=false

from LumensalisCP.Main.PreMainConfig import ImportProfiler
__triggersCommonSayImport = ImportProfiler("Triggers.common" )

__triggersCommonSayImport( "IOContext... " )
from LumensalisCP.IOContext  import *

from LumensalisCP.Triggers.Invocable import *

__triggersCommonSayImport( "Trigger... " )
from LumensalisCP.Triggers.Trigger import Trigger, TriggerActionType

__triggersCommonSayImport( "Action... " )
from LumensalisCP.Triggers.Action import Action, ActionDoArg, ActionCB, ActionCBArg, ActionSelectBehavior

#############################################################################

def ___fireOnSet( source:Optional[InputSource]=None, trigger:Optional[Trigger]=None ) -> Callable[..., Callable[[InputSource, EvaluationContext], None]]: #type: ignore
    assert source is not None
    # assert trigger is not None
    def on2( cb:Callable[[InputSource, EvaluationContext], None] ) -> Callable[[InputSource, EvaluationContext], None]:
        cTrigger = trigger or Trigger( name=cb.__name__ )
        #callable._trigger = cTrigger
        cTrigger.fireOnSet( source )
        cTrigger.addAction( cb ) # type: ignore
        return cb
    return on2

#############################################################################

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

#def fireOnClick( expression:Expression|ExpressionTerm,  target:Any, trigger:Optional[Trigger]=None ) -> Trigger:
#    return fireOnTrue( expression=expression, trigger=trigger, target=target )

def fireOnRising( expression:ExpressionTerm, target:Any, trigger:Optional[Trigger]=None ) -> Trigger:
    return fireOnTrue( expression= rising( expression ), trigger=trigger, target=target )

def fireOnFalling( expression:ExpressionTerm, target:Action, trigger:Optional[Trigger]=None ) -> Trigger:
    return fireOnTrue( expression= falling( expression ), trigger=trigger, target=target )

#############################################################################

__triggersCommonSayImport.complete()
