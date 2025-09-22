
try: 
    from typing import NewType, TypeAlias, TYPE_CHECKING # type: ignore

    
except ImportError:
    #TimeInSeconds = float  # type: ignore
    TYPE_CHECKING = False # type: ignore
    if not TYPE_CHECKING:
        def NewType(name:str, type_:type) : # type: ignore
            """Create a new type with the given name and type."""
            def convert(value): # type: ignore
                return type_(value)
            return convert # type: ignore
        
import time

TimeInSeconds = NewType('TimeInSeconds', float) # type: ignore


__getMonotonic = time.monotonic
__startTime = __getMonotonic() # type: ignore

def getOffsetNow()->TimeInSeconds:
    """ Get the current time"""
    return __getMonotonic() - __startTime # type: ignore

__all__ = [
    'getOffsetNow',
    'TimeInSeconds'
    ]
