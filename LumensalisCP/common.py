from LumensalisCP.CPTyping import Any, Callable, Generator, List, Mapping
from .Debug import Debuggable
TimeInSeconds = float
DegreesPerSecond = float
Degrees = float

def dictAddUnique( d:Mapping[str,Any], key:str, value:Any ) -> None:
    if key in d:
        assert d[key] == value
    else:
        d[key] = value
        

def updateKWDefaults( kwargs:Mapping, **updatedDefaults ) -> Mapping:
    for tag,val in updatedDefaults.items():
        if tag not in kwargs:
            kwargs[tag] = val
    return kwargs