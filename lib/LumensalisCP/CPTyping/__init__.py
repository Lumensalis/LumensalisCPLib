from __future__ import annotations
# pylint: disable=unused-import,import-error
#   pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayCPTypingImport = getImportProfiler( globals() ) # "CPTyping"

try:
	# imports used only for typing
    #import overrides
    
    from typing import TYPE_CHECKING
    from functools import wraps
    from typing import Any
    from typing import List,  Tuple, Sequence
    from typing import Generator, Iterable, Iterator
    from typing import Dict, Mapping, MutableMapping
    from typing import IO, TextIO
    from typing import Callable, ParamSpec, Protocol
    from typing import Union, ForwardRef, Required, NotRequired, Optional
    from typing import Unpack
    from typing import TypeAlias, NewType, Type
    from typing import Self 
    from typing import Type, TypeAlias, TypedDict, TypeVar
    from typing import ClassVar, Generic, Generator
    from typing import NoReturn
    from typing import final, overload, override
    from typing import Coroutine, Awaitable, AsyncGenerator, AsyncIterable, AsyncIterator
    from typing import ParamSpec, Concatenate
    try:
        from types import ModuleType    
    except ImportError:
        pass
        # ModuleType:TypeAlias = type(sys) # type: ignore

    # any imports below this won't happen if the error gets raised
    LCPF_TYPING_IMPORTED = True
    
    KWDS_TYPE:TypeAlias = Any # TypeAlias = dict[str, Any]  # keyword arguments dictionary
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
    TYPE_CHECKING = False # type: ignore

    if not TYPE_CHECKING:
        from LumensalisCP.CPTyping._pseudoTyping  import *
        
if LCPF_TYPING_IMPORTED:
    # this is _not_ within the initial try/except because we do
    # _not_ want to silently ignore errors
    raise NotImplementedError

StrAnyDict:TypeAlias = Dict[str,Any]
TracebackType: TypeAlias = Any

if TYPE_CHECKING:
    from .GenericT import GenericT
    

else: 
    class _GenericT:
        def __init__(self, cls:type) -> None: 
            self._cls = cls
        def __getitem__(self, item:Any): # pylint: disable=unused-argument
            return self._cls
    
    def GenericT(cls:type) ->type: 
        return _GenericT(cls) # type: ignore # pylint: disable=invalid-name


_sayCPTypingImport.complete(globals())
