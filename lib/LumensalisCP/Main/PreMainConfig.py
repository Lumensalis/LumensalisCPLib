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


if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager


class _MLCAnnotation:
    def __init__(self, message:str, *args:Any, **kwds:Any) -> None:

        self.message = message
        if len(args) > 0:
            try:
                self.message = message % args
            except : 
                self.message = self.message + " (could not format args)"
                
        self.kwds = kwds
        self.msecSinceStart = pmc_mainLoopControl.getMsSinceStart()
        if len(kwds) > 0:
            self.kwds = kwds

    def elapsedMs(self, prior:_MLCAnnotation) -> int:
        return prior.msecSinceStart - self.msecSinceStart

    def __repr__(self) -> str:
        return f"STARTUP @ {self.msecSinceStart/1000.0:0.3f}ms) : {self.message}"


class _MainLoopControl(object):
    
    def __init__(self):
        self.__started:int = supervisor.ticks_ms()
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
        self.prior_collect_period = None
        #self.main: = None
        
        self.min_delta_free = 32768
        self.__absoluteMinimumThreshold:int = 256000
        self.__actualFreeThreshold:int = 256000
        
        self.freeBuffer = None
        self.targetCollectPeriod:float|None = 0.15
        self.minCollectRatio = 0.0035
        
        self.verboseCollect = True
        self.freeAfterLastCollection = gc.mem_free() # pylint: disable=no-member

        
    def _setMain( self, main:MainManager ):
        self.main = main
    
    def setFreeThreshold(self, threshold:int ):
        self.__actualFreeThreshold = max( threshold, self.__absoluteMinimumThreshold )
        
    def setMinimumThreshold(self, threshold:int ):
        self.__absoluteMinimumThreshold  = threshold
        self.__actualFreeThreshold = max( self.__actualFreeThreshold, self.__absoluteMinimumThreshold )

    def checkAndRunCollection(self,
                      context:Optional[Any]=None,     # [unused-argument] # pylint: disable=unused-argument
                      force:bool = False, 
                      show:bool = False): 

        now = time.monotonic()
        mem_free_before = gc.mem_free()  # pylint: disable=no-member
        mem_free_beforeelapsed = time.monotonic() - now
        if mem_free_before > self.__actualFreeThreshold and not force:
            # print( f"GC free = {mem_free_before}" )
            if show:
                now = time.monotonic()
                mem_alloc_before = gc.mem_alloc()  # pylint: disable=no-member
                mem_alloc_beforeelapsed = time.monotonic() - now
                
                timeBeforeCollect = self.main.getNewNow()
                cycle = self.main.cycle
                delta_cycles = max( 1, cycle - self.priorCycle )
                currentMs = pmc_mainLoopControl.getMsSinceStart()
                elapsedSincePriorCollectMS = currentMs - self.priorMs
                delta_alloc = mem_alloc_before - self.prior_mem_alloc 
                delta_free = mem_free_before - self.prior_mem_free
                #print( f"cycle {cycle}, {len(main.timers.timers)}")
                elapsedSeconds = elapsedSincePriorCollectMS/1000.0
                if self.verboseCollect:
                    print( f"""GC per cycle = {
        elapsedSeconds/delta_cycles:0.03f}s, alloc={
        delta_alloc/delta_cycles:0.1f}, free={
        delta_free/delta_cycles:0.1f} skipping at {
        pmc_mainLoopControl.getMsSinceStart()/1000.0:0.3f} / {
        timeBeforeCollect:0.3f} [{cycle}],  free={
        mem_free_before} alloc={mem_alloc_before}, since last collect = {
        elapsedSincePriorCollectMS/1000.0:.3f} [{delta_cycles}] {
        delta_alloc} alloc, {delta_free} free gc.mem_f/a()={
        mem_free_beforeelapsed:.3f}/{mem_alloc_beforeelapsed:.3f}"""
                  )

            return
        
        now = time.monotonic()
        mem_alloc_before = gc.mem_alloc()  # pylint: disable=no-member
        mem_alloc_beforeelapsed = time.monotonic() - now
        if self.verboseCollect:
            sys.stdout.write( f"{now:.3f} GC collect " )
        
        # run collection
        timeBeforeCollect = self.main.getNewNow()
        gc.collect()
        timeAfterCollect = self.main.getNewNow()
        
        currentMs = pmc_mainLoopControl.getMsSinceStart()
        mem_alloc_after = gc.mem_alloc()  # pylint: disable=no-member
        mem_free_after = gc.mem_free()  # pylint: disable=no-member
        
        # calculate elapsed / deltas
        collectElapsed = timeAfterCollect-timeBeforeCollect
        
        elapsedSincePriorCollectMS = currentMs - self.priorMs
        elapsedSincePriorCollect = elapsedSincePriorCollectMS/1000.0

        cycle = self.main.cycle
        delta_alloc = mem_alloc_before-mem_alloc_after
        delta_free = mem_free_before - mem_free_after 
        delta_cycles = max( 1, cycle - self.priorCycle )
        collectRatio = collectElapsed / elapsedSincePriorCollect
        
        if self.verboseCollect :
            print( f" took {collectElapsed:.3f} of {elapsedSincePriorCollect:.3f} at {pmc_mainLoopControl.getMsSinceStart()/1000.0:0.3f} for {delta_cycles} cycles freeing {delta_alloc} ( {delta_alloc/delta_cycles:.1f} per cycle) leaving {mem_alloc_after} used, {mem_free_after} free t={self.__actualFreeThreshold} cr={collectRatio}  gc.mem_f/a()={mem_free_beforeelapsed:.3f}/{mem_alloc_beforeelapsed:.3f}" )

        if self.targetCollectPeriod is not None and collectElapsed > self.targetCollectPeriod:
            

            newThreshold = self.__actualFreeThreshold
            reason = "" # pylint: disable=unused-variable # type: ignore
            if - delta_free < self.min_delta_free:
                reason, newThreshold = "min_delta_free", mem_free_before - self.min_delta_free
                
            elif collectRatio > self.minCollectRatio:
                reason, newThreshold = "collect_ratio", mem_free_before + delta_free * 0.5
            #elif collectElapsed > self.prior_collect_period:
            #    reason, newThreshold = "prior_collect_period", mem_free_after - delta_free / 2 
            else:
                reason, newThreshold = "just cuz", newThreshold-1
                
            newThreshold = int( max( self.__absoluteMinimumThreshold, newThreshold ) )
            if  newThreshold != self.__actualFreeThreshold:
                try:
                    if self.main.enableDbgOut:
                        self.main.dbgOut( f"  (threshold changing {newThreshold - self.__actualFreeThreshold } from {self.__actualFreeThreshold} to {newThreshold} for {reason} df={delta_free}, cr={collectRatio})")
                except: pass # pylint: disable=bare-except
                
                self.__actualFreeThreshold = newThreshold


        self.priorMs = currentMs
        self.prior_mem_alloc = mem_alloc_after
        self.prior_mem_free = mem_free_after
        self.priorCycle = cycle
        self.prior_collect_period = collectElapsed
        

        #print( f"cycle {cycle}, {len(main.timers.timers)}")
        #print( f"GC collection at {timeBeforeCollect:0.3f} took {timeAfterCollect-timeBeforeCollect:.3f} of {elapsedSincePriorCollectMS/1000.0:.3f} for {delta_cycles} cycles freeing {delta_alloc} ( {delta_alloc/delta_cycles:.1f} per cycle) leaving {mem_alloc_after} used, {mem_free_after} free" )


assert globals().get('pmc_gcManager',None) is None, "pmc_gcManager already exists, cannot reinitialize"    

pmc_gcManager = GCManager()
pmc_mainLoopControl = _MainLoopControl()

def printElapsed(desc:str):
    gcUsed = gc.mem_alloc()  # pylint: disable=no-member
    gcFree = gc.mem_free() # pylint: disable=no-member
    print( "%s : %0.3f seconds since start | %r used, %r free | monotonic=%.03f" % 
          (desc,pmc_mainLoopControl.getMsSinceStart()/1000.0, 
           gcUsed, gcFree, time.monotonic()
           ) )

def sayAtStartup(desc:str, **kwds:Any) -> None:
    pmc_mainLoopControl.sayAtStartup(desc,**kwds)
    #print( f"Startup [{pmc_mainLoopControl.getMsSinceStart()/1000.0:.3f}]: {desc}" )

#############################################################################


__all__ = [ 'pmc_gcManager', 'pmc_mainLoopControl', 'printElapsed', 'sayAtStartup', ]
