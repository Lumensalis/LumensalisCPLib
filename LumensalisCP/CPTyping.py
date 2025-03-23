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
    Generator = None
    Tuple = None
    
    def override( f ): return f
