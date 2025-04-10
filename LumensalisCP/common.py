from LumensalisCP.CPTyping import Any, Callable, Generator, List, Mapping,TypedDict
from .Debug import Debuggable
import traceback

TimeInSeconds = float
DegreesPerSecond = float
Degrees = float
ZeroToOne = float
PlusMinusOne = float
Volts = float


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

import LumensalisCP.Main.Expressions

def toZeroToOne( value:Any ) -> ZeroToOne:
    if type(value) is float: return value
    if type(value) is bool:
        return 1.0 if value else 0.0
    if type(value) is object:
        if isinstance(value,LumensalisCP.Main.Expressions.InputSource):
            return float( value.value )

    try:
        return float(value)
    except Exception as inst:
        print( f"toZeroToOne exception {inst} for {value}/{getattr(value,'__name__',None)}" )
        raise

def SHOW_EXCEPTION( inst, fmt:str, **args ):
    print( f"EXCEPTION {inst} : {safeFmt(fmt,**args)}" )
    print( "\n".join(traceback.format_exception(inst)) )
    