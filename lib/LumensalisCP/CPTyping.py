from __future__ import annotations
# pylint: disable=unused-import,import-error
#   pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false
try:
	# imports used only for typing
    #import overrides
    from typing import Any
    from typing import List,  Tuple, Sequence
    from typing import Generator, Iterable, Iterator
    from typing import Dict, Mapping, MutableMapping
    from typing import IO, TextIO
    from typing import Callable, ParamSpec, Protocol
    from typing import Union, ForwardRef, Required, NotRequired, Optional
    from typing import Unpack
    from typing import TypeAlias, NewType
    from typing import Self 
    from typing import Type, TypeAlias, TypedDict, TypeVar
    from typing import ClassVar, Generic, Generator
    from typing import NoReturn
    
    from typing import final, overload, override
    
    from functools import wraps

    
    
    # any imports below this won't happen if the error gets raised
    LCPF_TYPING_IMPORTED = True
    
    KWDS_TYPE: TypeAlias = dict[str, Any]  # keyword arguments dictionary
    class PseudoTypingExpression(object): # type: ignore
        def __init__(self,*args:Any,**kwds:KWDS_TYPE):
            raise NotImplementedError    
    
    class PseudoTypingType(object):
        def __init__(self,*args:Any,**kwds:KWDS_TYPE):
            raise NotImplementedError
        
    def makeTypingExpression( a:Any ) -> Any : # type: ignore
        return a
    
    #def makeTypingExpression( a:Any ) -> Any : # type: ignore
    #    return a
    from weakref import ReferenceType

except ImportError:
    LCPF_TYPING_IMPORTED = False # type: ignore
    TYPE_CHECKING = False
    if not TYPE_CHECKING:
        from LumensalisCP._pseudoTyping import *
        
if LCPF_TYPING_IMPORTED:
    # this is _not_ within the initial try/except because we do
    # _not_ want to silently ignore errors
    raise NotImplementedError

StrAnyDict:TypeAlias = Dict[str,Any]
