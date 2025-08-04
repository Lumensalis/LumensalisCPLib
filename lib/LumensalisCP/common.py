from __future__ import annotations

# pylint: disable=unused-import,import-error
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

import traceback
import json
import math
import adafruit_itertools as itertools  # type: ignore # pylint: disable=import-error

#LumensalisCP.ImportProfiler import getImportProfiler
from LumensalisCP.ImportProfiler import getImportProfiler
_sayCommonImport = getImportProfiler( "common" )

#############################################################################

from LumensalisCP.Temporal.Time import getOffsetNow, TimeInSeconds 

from LumensalisCP.Main.PreMainConfig import  pmc_mainLoopControl, pmc_gcManager
from LumensalisCP.util.CountedInstance import CountedInstance
import LumensalisCP
from LumensalisCP.CPTyping import *
from LumensalisCP.Debug import Debuggable, IDebuggable

import LumensalisCP.pyCp.weakref as weakref

from LumensalisCP.Units import *

from LumensalisCP.Main.GetManager import getMainManager, getCurrentEvaluationContext

_sayCommonImport.parsing()


#############################################################################


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

def updateKWDefaults( kwargs:Any, #dict[str,Any], 
                     **updatedDefaults:dict[str,Any]) -> dict[str,Any]:
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

def safeRepr( v:Any ):
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

def toZeroToOne_( value:Any ) -> ZeroToOne:
    """ Convert a value to a float. If the value is already a float, it is returned as is.
    
    """
    if isinstance(value, float): return value
    if isinstance(value, bool):
        return 1.0 if value else 0.0

    try:
        return float(value) # type: ignore
    except Exception as inst:
        print( f"toZeroToOne exception {inst} for {value}/{getattr(value,'__name__',None)}" )
        raise


def toZeroToOne( value:Any ) -> ZeroToOne:
    """ Convert a value to a float. If the value is already a float, it is returned as is.
    
    """
    if isinstance(value,LumensalisCP.Inputs.InputSource):
        value = value.value  # type: ignore
    return toZeroToOne_(value)


def withinZeroToOne_( value:Any ) -> ZeroToOne:
    """ __summary__ 
    Convert a value to a float between 0.0 and 1.0 inclusive. If the value is already a float, it is clamped to the range.    
    """
    return max(0.0,min(1.0,toZeroToOne_(value)) )

def withinZeroToOne( value:Any ) -> ZeroToOne:
    """ __summary__ 
    Convert a value to a float between 0.0 and 1.0 inclusive. If the value is already a float, it is clamped to the range.    
    """
    return max(0.0,min(1.0,toZeroToOne(value)) )

def SHOW_EXCEPTION( inst:Exception, fmt:str, *args:Any ):
    print( f"EXCEPTION {inst} : {safeFmt(fmt,*args)}" )
    print( "\n".join(traceback.format_exception(inst)) )
    
_sayCommonImport.complete(globals())
