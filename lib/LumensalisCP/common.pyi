from __future__ import annotations

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
TimeInSeconds:TypeAlias  = float # Time in seconds
TimeSpanInSeconds:TypeAlias  = float #

DegreesPerSecond:TypeAlias  = float # rotation speed  in degrees per second
Degrees:TypeAlias  = float # angle in degrees
ZeroToOne:TypeAlias  = float # a value between 0.0 and 1.0 inclusive
PlusMinusOne:TypeAlias  = float # a value between -1.0 and 1.0 inclusive
Volts:TypeAlias  = float   # voltage in volts
Hertz:TypeAlias  = float   # frequency in cycles per second


def dictAddUnique( d:Dict[Any,Any], key:Any, value:Any ) -> None: ...


def updateKWDefaults( kwargs:Dict[str,Any], **updatedDefaults ) -> Dict[str,Any]: ...

def safeRepr( v ) -> str: ...
def safeFmt( fmtStr:str, *args:Any ) ->str: ...
    
class EnsureException(Exception): ...
    
def ensure( condition:bool, fmtStr:str|None = None, *args:Any ) -> None: ... # pylint: disable=keyword-arg-before-vararg

def toZeroToOne( value:Any ) -> float: ...
    
def withinZeroToOne( value:Any ) -> ZeroToOne: ...

def SHOW_EXCEPTION( inst:Exception, fmt:str, *args )-> None: ...

getMainManager: LumensalisCP.util.Singleton.Singleton[MainManager] 
