from __future__ import annotations
#from LumensalisCP.CPTyping import *
#from LumensalisCP.common import Debuggable
#from LumensalisCP.Inputs import InputSource

from LumensalisCP.IOContext  import *
from LumensalisCP.Triggers.Trigger import Trigger
#import functools

#############################################################################


#############################################################################


def fireOnSet( source:Optional[InputSource]=None, trigger:Optional[Trigger]=None ): #type: ignore
    assert source is not None
    # assert trigger is not None
    def on2( cb:Callable ):
        cTrigger = trigger or Trigger( name=cb.__name__ )
        #callable._trigger = cTrigger
        cTrigger.fireOnSet( source )
        cTrigger.addAction( cb  )
        return cb
    return on2



def fireOnTrue( expression:Expression|ExpressionTerm, target:Any, trigger:Optional[Trigger]=None ):
    # assert trigger is not None
    def on2( cb:Callable[..., Any], expression:Expression|ExpressionTerm=expression, trigger:Trigger|None=trigger ):

        cTrigger = trigger or Trigger( name=cb.__name__ )
        # @functools.wraps(callable)
        def wrapped(*args,**kwargs):
        
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


def fireOnClick( expression:Expression|ExpressionTerm, trigger:Optional[Trigger]=None ):
    return  fireOnTrue( expression=expression, trigger=trigger )

def fireOnRising( expression:ExpressionTerm, target:Any, trigger:Optional[Trigger]=None ):
    return  fireOnTrue( expression= rising( expression ), trigger=trigger, target=target )
