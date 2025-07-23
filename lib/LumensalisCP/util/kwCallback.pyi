from __future__ import annotations
from LumensalisCP.CPTyping import *

# pylint: disable=unused-import,import-error,unused-argument
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false
class KWCallback(object):
    """Wrapper for callback/closure
    
    CircuitPython/MicroPython does not support introspection to determine 
    what *positional and **kwd arguments are valid / required.  So, this
    wrapper will catch the exceptions generated in those cases and "remember"
    to remove the arguments for future calls.
    
    
>>> from LumensalisCP.util.kwCallback import KWCallback, KWCallbackArg
>>> def foo( bar = 2 ):
    print( f"bar = {bar}" )
    
>>> foo( baz = 3 )
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unexpected keyword argument 'baz'
>>> k = KWCallback( foo )
>>> k( baz = 3 )
bar = 2
>>> 

    Args:
        object (_type_): _description_
    """
    
    requiredKwds = None
    
    @classmethod
    def make( cls, cb:Callable[..., Any], **kwds:dict[str,Any] ) -> KWCallback: ...
        
    def __init__( self, cb:Callable[..., Any], name:Optional[str]=None, requiredKwds:Optional[List[str]] = None ) -> None: ...
        
    def __call__( self, *args:Any, **kwds:dict[str,Any] ) -> Any: ...

        
KWCallbackArg:TypeAlias = Callable[..., Any]  # type: ignore        
