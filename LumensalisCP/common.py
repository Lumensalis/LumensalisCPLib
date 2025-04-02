from LumensalisCP.CPTyping import Any, Callable, Generator, List, Mapping,TypedDict
from .Debug import Debuggable
TimeInSeconds = float
DegreesPerSecond = float
Degrees = float
ZeroToOne = float

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

def safeFmt( fmtStr:str, *args:Any ):
    try:
        try:
            return fmtStr % args
        except Exception as inst:
            return "safeFmt( %r, ... ) failed : %s" % (fmtStr, inst )
    except:
        return "safeFmt failed"
    
class EnsureException(Exception):
    pass
    
    
def ensure( condition:bool, fmtStr:str|None = None, *args:Any ):
    if not condition:
        if fmtStr is None:
            raise EnsureException( "ensure failed" )
        raise EnsureException( safeFmt( fmtStr, *args ) )