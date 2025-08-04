
try: 
    from typing import NewType, TypeAlias, TYPE_CHECKING

    
except ImportError:
    #TimeInSeconds = float  # type: ignore
    TYPE_CHECKING = False
    if not TYPE_CHECKING:
        def NewType(name:str, type_:type) : # type: ignore
            """Create a new type with the given name and type."""
            def convert(value): # type: ignore
                return type_(value)
            return convert # type: ignore
        
import time

TimeInSeconds = NewType('TimeInSeconds', float)


__getMonotonic = time.monotonic
__startTime = __getMonotonic() # type: ignore

def getOffsetNow()->TimeInSeconds:
    """ Get the current time"""
    return __getMonotonic() - __startTime # type: ignore

__all__ = [
    'getOffsetNow',
    'TimeInSeconds'
    ]
