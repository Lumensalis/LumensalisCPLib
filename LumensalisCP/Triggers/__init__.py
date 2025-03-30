from LumensalisCP.CPTyping import *
from LumensalisCP.common import Debuggable
from LumensalisCP.Main.Expressions import InputSource, UpdateContext, Expression, ExpressionTerm
from .Trigger import Trigger
#import functools

#############################################################################


#############################################################################


def fireOnSet( source:InputSource=None, trigger:Trigger=None ):
    assert source is not None
    # assert trigger is not None
    def on2( callable:Callable ):
        cTrigger = trigger or Trigger( name=callable.__name__ )
        callable._trigger = cTrigger
        cTrigger.fireOnSet( source, callable )
        return callable
    return on2


def fireOnTrue( expression:Expression|ExpressionTerm, trigger:Trigger=None ):
    # assert trigger is not None
    def on2( callable:Callable, expression=expression, trigger=trigger ):

        cTrigger = trigger or Trigger( name=callable.__name__ )
        # @functools.wraps(callable)
        def wrapped(*args,**kwargs):
        
            result = callable(*args, **kwargs)

            return result 
        setattr(callable, 'trigger', cTrigger )
        setattr(callable,'expression', expression )        
        setattr(wrapped, 'trigger', cTrigger )
        setattr(wrapped,'expression', expression )
        #setattr( wrapped, '__name__', callable.__name__ )
        
        cTrigger.addAction( wrapped )
        cTrigger.fireOnTrue( expression )
        print( f"wrapped for {callable.__name__} = {wrapped}, class={wrapped.__class__}")
        return cTrigger
    return on2