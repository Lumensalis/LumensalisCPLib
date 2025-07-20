import traceback
import json
import math

import adafruit_itertools as itertools  # type: ignore # pylint: disable=import-error

import LumensalisCP
from LumensalisCP.Debug import Debuggable
from LumensalisCP.CPTyping import *
import LumensalisCP.util.Singleton 
import LumensalisCP.pyCp.weakref as weakref

# Common types used throughout the library
# 
TimeInNS:TypeAlias =  int # Time in nanoseconds
TimeSpanInNS:TypeAlias  = int # Time span in nanoseconds
TimeInMS:TypeAlias  = int # Time in milliseconds
TimeSpanInMS:TypeAlias  = int # Time span in milliseconds
TimeInSeconds:TypeAlias  = float # Time in seconds
TimeSpanInSeconds:TypeAlias  = float #

DegreesPerSecond:TypeAlias  = float # rotation speed  in degrees per second
Degrees:TypeAlias  = float # angle in degrees
ZeroToOne:TypeAlias  = float # a value between 0.0 and 1.0 inclusive
PlusMinusOne:TypeAlias  = float # a value between -1.0 and 1.0 inclusive
Volts:TypeAlias  = float   # voltage in volts
Hertz:TypeAlias  = float   # frequency in cycles per second


def dictAddUnique( d:Dict[Any,Any], key:Any, value:Any ) -> None:
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

def updateKWDefaults( kwargs:Dict[str,Any], **updatedDefaults ) -> Dict[str,Any]:
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

def safeRepr( v ):
    try:
        return repr(v)
    except Exception as inst: # pylint: disable=broad-exception-caught
        return f"SAFEREPR( {type(v)}@{id(v)} : {inst} / {traceback.format_exception(inst)} )"

def safeFmt( fmtStr:str, *args:Any ):
    """ A safe formatting function that returns a formatted string or an error message if formatting fails.
    """
    try:
        try:
            return fmtStr % args
        except Exception as inst: # pylint: disable=broad-exception-caught
            return "safeFmt( %r, ... ) failed : %s %r" % (fmtStr, inst, traceback.format_exception(inst) )
    except: # pylint: disable=bare-except
        return "safeFmt failed"
    
class EnsureException(Exception):
    """_summary_
    base class for exceptions raised by the ensure function.
    Args:
        Exception (_type_): _description_
    """
    
    
def ensure( condition:bool, fmtStr:str|None = None, *args:Any ):  # pylint: disable=keyword-arg-before-vararg
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

try:
    import typing
    if TYPE_CHECKING:
        import LumensalisCP.Inputs
except ImportError:
    pass

def toZeroToOne( value:Any ) -> float:
    """ Convert a value to a float. If the value is already a float, it is returned as is.
    
    """
    if isinstance(value, float): return value
    if isinstance(value, bool):
        return 1.0 if value else 0.0

    try:
    
        if isinstance(value,LumensalisCP.Inputs.InputSource):
            return float( value.value )  # type: ignore

        return float(value) # type: ignore
    except Exception as inst:
        print( f"toZeroToOne exception {inst} for {value}/{getattr(value,'__name__',None)}" )
        raise

def withinZeroToOne( value:Any ) -> ZeroToOne:
    """ __summary__ 
    Convert a value to a float between 0.0 and 1.0 inclusive. If the value is already a float, it is clamped to the range.    
    """
    return max(0.0,min(1.0,toZeroToOne(value)) )

def SHOW_EXCEPTION( inst, fmt:str, *args ):
    print( f"EXCEPTION {inst} : {safeFmt(fmt,*args)}" )
    print( "\n".join(traceback.format_exception(inst)) )
    
    
getMainManager = LumensalisCP.util.Singleton.Singleton("MainManager")
#import LumensalisCP.Main.Expressions
