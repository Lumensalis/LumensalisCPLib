from __future__ import annotations

# pylint: disable=unused-import,import-error
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

import traceback
import json
import math
import adafruit_itertools as itertools  # type: ignore # pylint: disable=import-error

# pylint: disable=unused-argument

import LumensalisCP

from LumensalisCP.CPTyping import *
from LumensalisCP.Debug import Debuggable
import LumensalisCP.pyCp.weakref as weakref
from LumensalisCP.Main.Manager import MainManager
import LumensalisCP.util.Singleton 

# Common types used throughout the library
# 
TimeInNS:TypeAlias =  int # Time in nanoseconds
TimeSpanInNS:TypeAlias  = int # Time span in nanoseconds
TimeInMS:TypeAlias  = int # Time in milliseconds
TimeSpanInMS:TypeAlias  = int # Time span in milliseconds
TimeInSeconds = NewType('TimeInSeconds', float ) # Time in seconds
TimeSpanInSeconds:TypeAlias  = float #

TimeInSecondsConfigArg:TypeAlias = Union[TimeInSeconds, int, float]
def TimeInSecondsConfig( v:TimeInSecondsConfigArg|None, default:Optional[TimeInSecondsConfigArg] = None ) -> TimeInSeconds: ...

DegreesPerSecond:TypeAlias  = float # rotation speed  in degrees per second
Degrees:TypeAlias  = float # angle in degrees

ZeroToOne:TypeAlias  = float # a value between 0.0 and 1.0 inclusive
PlusMinusOne:TypeAlias  = float # a value between -1.0 and 1.0 inclusive
Volts:TypeAlias  = float   # voltage in volts
Hertz:TypeAlias  = float   # frequency in cycles per second

def dictAddUnique( d:dict[Any,Any], key:Any, value:Any ) -> None: ...

def updateKWDefaults[T]( kwargs:T|Any,
                     **updatedDefaults:dict[str,Any]) -> T: ... # type: ignore

def safeRepr( v:Any ) -> str: ...
def safeFmt( fmtStr:str, *args:Any ) ->str: ...
    
class EnsureException(Exception): ...
    
def ensure( condition:bool, fmtStr:str|None = None, *args:Any ) -> None: ... # pylint: disable=keyword-arg-before-vararg

def toZeroToOne( value:Any ) -> float: ...
    
def withinZeroToOne( value:Any ) -> ZeroToOne: ...

def SHOW_EXCEPTION( inst:Exception, fmt:str, *args:Any )-> None: ...

getMainManager: LumensalisCP.util.Singleton.Singleton[MainManager] 
