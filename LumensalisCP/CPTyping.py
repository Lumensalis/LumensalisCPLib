try:
	# imports used only for typing
    from typing import Tuple # <- this line causes the error
    import overrides
    from typing import *
    # any imports below this won't happen if the error gets raised
    #from circuitpython_typing import ReadableBuffer
    # from busio import I2C
except ImportError:
    
    pass # ignore the error
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
