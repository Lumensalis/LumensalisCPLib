from LumensalisCP.CPTyping import Any, Callable, Generator, List, Mapping,TypedDict
from .Debug import Debuggable
import traceback

import LumensalisCP.util.weakrefish as weakref

# Common types used throughout the library

# 
TimeInNS = int # Time in nanoseconds
TimeSpanInNS = int # Time span in nanoseconds
TimeInMS = int # Time in milliseconds
TimeSpanInMS = int # Time span in milliseconds
TimeInSeconds = float # Time in seconds
TimeSpanInSeconds = float #

DegreesPerSecond = float # rotation speed  in degrees per second
Degrees = float # angle in degrees
ZeroToOne = float # a value between 0.0 and 1.0 inclusive
PlusMinusOne = float # a value between -1.0 and 1.0 inclusive
Volts = float   # voltage in volts


def dictAddUnique( d:Mapping[str,Any], key:str, value:Any ) -> None:
    """_summary_
add a unique key/value pair to a dictionary, or assert that the key is already present with the same value.
    Args:
        d (Mapping[str,Any]): target dictionary
        key (str): key to add
        value (Any): value to add
    """
    if key in d:
        assert d[key] == value
    else:
        d[key] = value

def updateKWDefaults( kwargs:Mapping, **updatedDefaults ) -> Mapping:
    """_summary_

    Args:
        kwargs (Mapping): keyword dictionary/mapping to update  
        **updatedDefaults: keyword arguments to update the defaults with
        

    Returns:
        Mapping: the modified kwargs
    """
    for tag,val in updatedDefaults.items():
        if tag not in kwargs:
            kwargs[tag] = val
    return kwargs

def safeFmt( fmtStr:str, *args:Any ):
    """ A safe formatting function that returns a formatted string or an error message if formatting fails.
    """
    try:
        try:
            return fmtStr % args
        except Exception as inst:
            return "safeFmt( %r, ... ) failed : %s" % (fmtStr, inst )
    except:
        return "safeFmt failed"
    
class EnsureException(Exception):
    """_summary_
    base class for exceptions raised by the ensure function.
    Args:
        Exception (_type_): _description_
    """
    pass
    
    
def ensure( condition:bool, fmtStr:str|None = None, *args:Any ):
    """_summary_
    Throw an EnsureException if the condition is not met.

    Args:
        condition (bool): condition value to test
        fmtStr (str | None, optional): _description_. Defaults to None.

    Raises:
        EnsureException: _description_
    """
    if not condition:
        if fmtStr is None:
            raise EnsureException( "ensure failed" )
        raise EnsureException( safeFmt( fmtStr, *args ) )

import LumensalisCP.Main.Expressions

def toZeroToOne( value:Any ) -> float:
    """ Convert a value to a float. If the value is already a float, it is returned as is.
    
    """
    if type(value) is float: return value
    if type(value) is bool:
        return 1.0 if value else 0.0
    if type(value) is object:
        if isinstance(value,LumensalisCP.Inputs.InputSource):
            return float( value.value )

    try:
        return float(value)
    except Exception as inst:
        print( f"toZeroToOne exception {inst} for {value}/{getattr(value,'__name__',None)}" )
        raise

def withinZeroToOne( value:Any ) -> ZeroToOne:
    """ __summary__ 
    Convert a value to a float between 0.0 and 1.0 inclusive. If the value is already a float, it is clamped to the range.    
    """
    return max(0.0,min(1.0,toZeroToOne(value)) )

def SHOW_EXCEPTION( inst, fmt:str, **args ):
    print( f"EXCEPTION {inst} : {safeFmt(fmt,**args)}" )
    print( "\n".join(traceback.format_exception(inst)) )
    