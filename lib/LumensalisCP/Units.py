from __future__ import annotations
# Common types used throughout the library

from LumensalisCP.CPTyping import TypeAlias, NewType, Union,Optional

ZeroToOne:TypeAlias  = float # a value between 0.0 and 1.0 inclusive
PlusMinusOne:TypeAlias  = float # a value between -1.0 and 1.0 inclusive

TimeInNS:TypeAlias =  int # Time in nanoseconds
TimeSpanInNS:TypeAlias  = int # Time span in nanoseconds

TimeInMS:TypeAlias  = int # Time in milliseconds
TimeSpanInMS:TypeAlias  = int # Time span in milliseconds

TimeInSeconds = NewType('TimeInSeconds', float ) # Time in seconds
TimeSpanInSeconds:TypeAlias  = float #

DegreesPerSecond:TypeAlias  = float # rotation speed  in degrees per second
Degrees:TypeAlias  = float # angle in degrees

Volts:TypeAlias  = float   # voltage in volts
Hertz:TypeAlias  = float   # frequency in cycles per second


TimeInSecondsConfigArg:TypeAlias = Union[TimeInSeconds, int, float]
def TimeInSecondsConfig( v:TimeInSecondsConfigArg|None, default:Optional[TimeInSecondsConfigArg] = None ) -> TimeInSeconds:
    if v is None:
        assert default is not None, "TimeInSecondsConfig requires a value or a default"
        v = default
    return v # type: ignore
