############################################################################
## INTERNAL USE ONLY
""" provides settings for MainManager / gc logic / etc

Intended to allow configuration of internal diagnostics, by importing
_first_, modifying as desired, and then continuing as normal.

For example, in **code.py** :
```python
from LumensalisCP.Main.PreMainConfig import pmc_gcManager, pmc_mainLoopControl
pmc_mainLoopControl.ENABLE_PROFILE = True
pmc_gcManager.PROFILE_MEMORY = True

from LumensalisCP.Simple import *
main = ProjectManager()
# ...
```

MUST NOT IMPORT ANY OTHER LUMENSALIS FILES    
"""
from __future__ import annotations

# pylint: disable=missing-function-docstring, missing-class-docstring, missing-module-docstring
# pyright: reportPrivateUsage=false, reportUnusedImport=false, reportUnusedFunction=false

try:
    from typing import TYPE_CHECKING, Any,Optional, ClassVar
except ImportError:
    
    TYPE_CHECKING = False # type: ignore
    
import gc # type: ignore
import sys
import time
import supervisor

from LumensalisCP.util.CountedInstance import CountedInstance
from LumensalisCP.Temporal.Time import getOffsetNow, TimeInSeconds
from  LumensalisCP.Main import PreMainConfigRL as _pmc_rl

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager


class _MLCAnnotation(CountedInstance):
    def __init__(self, message:str, *args:Any, prefix:Optional[str]=None, **kwds:Any) -> None:
        super().__init__()
        self.msecSinceStart = pmc_mainLoopControl.getMsSinceStart()
        self.message = message
        if len(kwds) > 0:
            self.kwds = kwds
        if prefix is not None:
            self.prefix = prefix
    
        if len(args) > 0:
            try:
                self.message = message % args
            except : 
                self.message = self.message + " (could not format args)"

    @property
    def when(self) -> float:
        return self.msecSinceStart / 1000.0
    
    def elapsedMs(self, prior:_MLCAnnotation) -> int:
        return prior.msecSinceStart - self.msecSinceStart

    def __repr__(self) -> str:
        return _pmc_rl._MLCAnnotation__repr__(self)
        

class _MainLoopControl(object):
    __started:int

    def __init__(self):
        assert getattr(_MainLoopControl,'__started',None) is None, "pmc_mainLoopControl already exists, cannot reinitialize"
        _MainLoopControl.__started = supervisor.ticks_ms()
        self.__started:int = _MainLoopControl.__started 
        self.MINIMUM_LOOP:bool = False
        self.ENABLE_PROFILE:bool = False
        self.nextWaitPeriod:float = 0.01
        self.profileTimings:int = 10
        self.printStatCycles:int = 5000
        self.enableHttpDebug:bool = False
        self.preMainVerbose:bool = False
        self.startupVerbose:bool = True
        self.annotations:list[_MLCAnnotation] = []

    def getMsSinceStart(self):
        now = supervisor.ticks_ms()
        if now < self.__started:
            self.__started = now
        return now - self.__started

    def _sayMain(self, desc:str, *args:Any, **kwds:Any) -> _MLCAnnotation:
        annotation = _MLCAnnotation( desc, *args, **kwds ) 
        self.annotations.append( annotation )
        print( annotation )
        return annotation

    def sayAtStartup(self, desc:str, *args:Any, **kwds:Any) -> _MLCAnnotation:
        annotation = _MLCAnnotation( desc, *args, **kwds ) 
        self.annotations.append( annotation )
        print( annotation )
        return annotation

    def sayDebugAtStartup(self, desc:str, *args:Any,  **kwds:Any) -> _MLCAnnotation:
        annotation = _MLCAnnotation( desc, *args, **kwds ) 
        self.annotations.append( annotation )
        if self.startupVerbose: 
            print( annotation )
        return annotation

pmc_mainLoopControl = _MainLoopControl()

class GCManager(object):
    main:MainManager # type: ignore   # pylint: disable=no-member 
    
    def __init__(self):
        self.PROFILE_MEMORY:bool = False
        self.PROFILE_MEMORY_NESTED:bool = False
        self.PROFILE_MEMORY_ENTRIES:bool = False
        self.SHOW_ZERO_ALLOC_ENTRIES:bool = True
    
        self.printDumpInterval = 28
        self.collectionCheckInterval = 3.1
        self.showRunCollection = False

        self.priorCycle = 0
        self.priorMs = 0
        self.prior_mem_alloc = 0
        self.prior_mem_free = 0
        self.prior_collect_period:float|None = None
        #self.main: = None
        
        self.min_delta_free = 32768
        self.__absoluteMinimumThreshold:int = 768000
        self.__actualFreeThreshold:int = 768000
        
        self.freeBuffer = None
        self.targetCollectPeriod:float|None = 0.15
        self.minCollectRatio = 0.0035
        
        self.verboseCollect = True
        self.freeAfterLastCollection = gc.mem_free() # pylint: disable=no-member

        
    def _setMain( self, main:MainManager ):
        self.main = main
    
    def setFreeThreshold(self, threshold:int ) -> None:
        _pmc_rl.GCManager_setFreeThreshold(self,threshold)
        
    def setMinimumThreshold(self, threshold:int ) -> None:
        _pmc_rl.GCManager_setMinimumThreshold(self,threshold)

    def adjustLowerThreshold(self, reason:str) -> None:
        _pmc_rl.GCManager_adjustLowerThreshold(self, reason)

    def sayGC( self, message:str) -> None:
        _pmc_rl.GCManager_sayGC(self, message)


    def checkAndRunCollection(self,
                      context:Optional[Any]=None,     # [unused-argument] # pylint: disable=unused-argument
                      force:bool = False, 
                      show:bool = False) -> None: 
        _pmc_rl.GCManager_checkAndRunCollection(self, context,force,show)

assert globals().get('pmc_gcManager',None) is None, "pmc_gcManager already exists, cannot reinitialize"    

pmc_gcManager = GCManager()

_pmc_rl._setPMCGlobals( pmc_gcManager, pmc_mainLoopControl )

def printElapsed(desc:str):
    _pmc_rl._printElapsed(pmc_mainLoopControl.getMsSinceStart()/1000.0, desc)

def sayAtStartup(desc:str, **kwds:Any) -> None:
    pmc_mainLoopControl.sayAtStartup(desc,**kwds)
    #print( f"Startup [{pmc_mainLoopControl.getMsSinceStart()/1000.0:.3f}]: {desc}" )

#############################################################################


__all__ = [ 'pmc_gcManager', 'pmc_mainLoopControl', 'printElapsed', 'sayAtStartup', ]
