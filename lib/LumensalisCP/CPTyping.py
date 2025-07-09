from __future__ import annotations

try:
	# imports used only for typing
    #import overrides
    from typing import *
    from typing import IO
    # any imports below this won't happen if the error gets raised
    LCPF_TYPING_IMPORTED = True
except ImportError:
    
    pass # ignore the error
    #TYPE_CHECKING - False
    LCPF_TYPING_IMPORTED = False
    ForwardRef = None
    Any = None
    
    Callable = None
    Mapping = None
    List = None
    Dict = None
    Generator = None
    Tuple = None
    Required = None
    NotRequired = None
    Optional = None
    
    class __TDM(object):
        def __new__(cls, name, bases, ns, total=True):
            pass
    
    #def TypedDict(typename, *args, fields=None, total=True, **kwargs):
    #    return __TDM
    
    #_TypedDict = type.__new__(__TDM, 'TypedDict', (), {})
    #TypedDict.__mro_entries__ = lambda bases: (_TypedDict,)
    #TypedDict.__mro_entries__ = lambda bases: ()

    class TypedDict(object):
        pass
    
    
    def overload( f ): return f
    def override( f ): return f
    def final( f ): return f


if LCPF_TYPING_IMPORTED:
    # this is _not_ within the initial try/except because we do
    # _not_ want to silently ignore errors
    raise NotImplemented
    import abc
    