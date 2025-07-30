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

try:
    from typing import TYPE_CHECKING, Any,Optional
except ImportError:
    
    TYPE_CHECKING = False # type: ignore
    
import gc # type: ignore
import sys
import time
import supervisor

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager

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
        
    def getMsSinceStart(self):
        now = supervisor.ticks_ms()
        if now < self.__started:
            self.__started = now
        return now - self.__started

        
class GCManager(object):
    main:MainManager # type: ignore   # pylint: disable=no-member 
    
    def __init__(self):
        self.PROFILE_MEMORY:bool = False
        self.PROFILE_MEMORY_NESTED:bool = False
        self.PROFILE_MEMORY_ENTRIES:bool = False
        self.SHOW_ZERO_ALLOC_ENTRIES:bool = True
    
        self.priorCycle = 0
        self.priorMs = 0
        self.prior_mem_alloc = 0
        self.prior_mem_free = 0
        self.prior_collect_period = None
        #self.main: = None
        
        self.min_delta_free = 32768
        self.__absoluteMinimumThreshold:int = 128000
        self.__actualFreeThreshold:int = 128000
        
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
        
    def runCollection(self, 
                      context:Optional[Any]=None,     # [unused-argument] # pylint: disable=unused-argument
                      force:bool = False, 
                      show:bool = False): 

        now = time.monotonic()
        mem_free_before = gc.mem_free()  # pylint: disable=no-member
        mem_free_before_elapsed = time.monotonic() - now
        if mem_free_before > self.__actualFreeThreshold and not force:
            # print( f"GC free = {mem_free_before}" )
            if show:
                now = time.monotonic()
                mem_alloc_before = gc.mem_alloc()  # pylint: disable=no-member
                mem_alloc_before_elapsed = time.monotonic() - now
                
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
        mem_free_before_elapsed:.3f}/{mem_alloc_before_elapsed:.3f}"""
                  )

            return
        
        now = time.monotonic()
        mem_alloc_before = gc.mem_alloc()  # pylint: disable=no-member
        mem_alloc_before_elapsed = time.monotonic() - now
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
            print( f" took {collectElapsed:.3f} of {elapsedSincePriorCollect:.3f} at {pmc_mainLoopControl.getMsSinceStart()/1000.0:0.3f} for {delta_cycles} cycles freeing {delta_alloc} ( {delta_alloc/delta_cycles:.1f} per cycle) leaving {mem_alloc_after} used, {mem_free_after} free t={self.__actualFreeThreshold} cr={collectRatio}  gc.mem_f/a()={mem_free_before_elapsed:.3f}/{mem_alloc_before_elapsed:.3f}" )

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

pmc_gcManager = GCManager()
pmc_mainLoopControl = _MainLoopControl()

def printElapsed(desc:str):
    gcUsed = gc.mem_alloc()  # pylint: disable=no-member
    gcFree = gc.mem_free() # pylint: disable=no-member
    print( "%s : _mlc.getMsSinceStart()=%0.3f | %r used, %r free" % 
          (desc,pmc_mainLoopControl.getMsSinceStart()/1000.0, 
           gcUsed, gcFree
           ) )
    

def sayAtStartup(desc:str) -> None:
    print( f"Startup [{pmc_mainLoopControl.getMsSinceStart()/1000.0:.3f}]: {desc}" )

class ImportProfiler(object):
    """ A simple profiler for imports, to help identify slow imports """
    SHOW_IMPORTS:bool = False

    NESTING:list[ImportProfiler] = []
    def __init__(self, name:str ) -> None:
        self.name = name
        self.path = "->".join(  [i.name for i in ImportProfiler.NESTING] )
        
        self( "import starting")
        ImportProfiler.NESTING.append( self )
        
    def __call__(self, desc:str) -> None:
        if self.SHOW_IMPORTS:
            sayAtStartup( f"IMPORT {self.path} | {self.name} : {desc}" )

    def parsing(self) -> None:
        self( "parsing" )

    def complete(self) -> None:
        self( "import complete" )
        end = ImportProfiler.NESTING.pop()
        assert end is self, f"ImportProfiler nesting mismatch: {end.name} != {self.name}"

class ReloadableImportProfiler(ImportProfiler):
    SHOW_IMPORTS:bool = True
    pass 

__all__ = [ 'pmc_gcManager', 'pmc_mainLoopControl', 'printElapsed', 'sayAtStartup','ImportProfiler', 'ReloadableImportProfiler' ]
