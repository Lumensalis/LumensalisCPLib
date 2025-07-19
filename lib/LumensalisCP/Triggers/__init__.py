#from LumensalisCP.CPTyping import *
#from LumensalisCP.common import Debuggable
#from LumensalisCP.Inputs import InputSource

from LumensalisCP.IOContext  import *
from LumensalisCP.Main.Expressions import Expression, ExpressionTerm, rising
from .Trigger import Trigger
#import functools

#############################################################################


#############################################################################


def fireOnSet( source:Optional[InputSource]=None, trigger:Optional[Trigger]=None ):
    assert source is not None
    # assert trigger is not None
    def on2( callable:Callable ):
        cTrigger = trigger or Trigger( name=callable.__name__ )
        #callable._trigger = cTrigger
        cTrigger.fireOnSet( source )
        cTrigger.addAction( callable  )
        return callable
    return on2



def fireOnTrue( expression:Expression|ExpressionTerm, target=None, trigger:Optional[Trigger]=None ):
    # assert trigger is not None
    def on2( callable:Callable, expression=expression, trigger=trigger ):

        cTrigger = trigger or Trigger( name=callable.__name__ )
        # @functools.wraps(callable)
        def wrapped(*args,**kwargs):
        
            result = callable(*args, **kwargs)

            return result 
        try: setattr(callable, 'trigger', cTrigger )
        except: pass
        try: setattr(callable,'expression', expression )
        except: pass
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

def fireOnRising( expression:Expression|ExpressionTerm, target=None, trigger:Optional[Trigger]=None ):
    return  fireOnTrue( expression= rising( expression ), trigger=trigger, target=target )
