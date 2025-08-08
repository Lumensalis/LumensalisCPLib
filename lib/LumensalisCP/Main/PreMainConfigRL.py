############################################################################
## INTERNAL USE ONLY
from __future__ import annotations

# pylint: disable=missing-function-docstring, missing-class-docstring, missing-module-docstring
# pyright: reportPrivateUsage=false, reportUnusedImport=false, reportUnusedFunction=false

try:
    from typing import TYPE_CHECKING, Any,Optional, ClassVar
except ImportError:
    
    TYPE_CHECKING = False # type: ignore
    
import gc # type: ignore

from LumensalisCP.util.CountedInstance import CountedInstance
from LumensalisCP.Temporal.Time import getOffsetNow, TimeInSeconds

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    from LumensalisCP.Main.PreMainConfig import GCManager, _MLCAnnotation, _MainLoopControl

#############################################################################

pmc_gcManager:GCManager
pmc_mainLoopControl:_MainLoopControl

def _setPMCGlobals(  gcm:GCManager, mlc:_MainLoopControl) -> None:
    global pmc_gcManager, pmc_mainLoopControl
    pmc_gcManager = gcm
    pmc_mainLoopControl = mlc

def _MLCAnnotation__repr__(self:_MLCAnnotation) -> str:
        return f"{getattr(self,'prefix','STARTUP')} @ {self.when:0.3f}) : {self.message}"

def GCManager_sayGC(self:GCManager, message:str) -> None:
    pmc_mainLoopControl._sayMain( message, prefix='GC')

def GCManager_adjustLowerThreshold(self:GCManager, reason:str) -> None:
    self.sayGC(f"Adjusting lower threshold: {reason}" )
    before_free = gc.mem_free()
    before_alloc = gc.mem_alloc()
    self.sayGC(f"  collecting (before free={before_free}, alloc={before_alloc})")
    gc.collect()
    after_free = gc.mem_free()
    after_alloc = gc.mem_alloc()
    self.sayGC(f"  (after free={after_free}, alloc={after_alloc})")
    delta = before_free - after_free
    newThreshold = after_free - max( delta, 512000 )
    self.sayGC(f"lower threshold set to {newThreshold}: {reason}" )
    self.setFreeThreshold(newThreshold)

def GCManager_setFreeThreshold(self:GCManager, threshold:int ) -> None:
    newThreshold =  max( threshold, self.__absoluteMinimumThreshold )
    if newThreshold != self.__actualFreeThreshold:
        self.sayGC(f"freeThreshold changing from {self.__actualFreeThreshold} to {newThreshold}")
        self.__actualFreeThreshold = newThreshold
    

def GCManager_setMinimumThreshold(self:GCManager, threshold:int ) -> None:
    self.__absoluteMinimumThreshold  = threshold
    self.__actualFreeThreshold = max( self.__actualFreeThreshold, self.__absoluteMinimumThreshold )

def GCManager_checkAndRunCollection(self:GCManager,
                      context:Optional[Any]=None,     # [unused-argument] # pylint: disable=unused-argument
                      force:bool = False, 
                      show:bool = False) -> None: 
    
    
    now = getOffsetNow()
    mem_free_before = gc.mem_free()  # pylint: disable=no-member
    mem_free_beforeelapsed = getOffsetNow() - now
    if mem_free_before > self.__actualFreeThreshold and not force:
        # print( f"GC free = {mem_free_before}" )
        if show:
            now = getOffsetNow()
            mem_alloc_before = gc.mem_alloc()  # pylint: disable=no-member
            mem_alloc_beforeelapsed = getOffsetNow() - now
            
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
    
    now = getOffsetNow()
    mem_alloc_before = gc.mem_alloc()  # pylint: disable=no-member
    mem_alloc_beforeelapsed = getOffsetNow() - now
    #if self.verboseCollect:
    #    sayAtStartup( f"{now:.3f} GC collect " )
    
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
        self.sayGC( f"collect took {collectElapsed:.3f} of {elapsedSincePriorCollect:.3f} at {pmc_mainLoopControl.getMsSinceStart()/1000.0:0.3f} for {delta_cycles} cycles freeing {delta_alloc} ( {delta_alloc/delta_cycles:.1f} per cycle) leaving {mem_alloc_after} used, {mem_free_after} free t={self.__actualFreeThreshold} cr={collectRatio}  gc.mem_f/a()={mem_free_beforeelapsed:.3f}/{mem_alloc_beforeelapsed:.3f}" )

    if False:
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
    


def _printElapsed(when:float,desc:str):
    gcUsed = gc.mem_alloc()  # pylint: disable=no-member
    gcFree = gc.mem_free() # pylint: disable=no-member
    print( "%s : %0.3f seconds since start | %r used, %r free | monotonic=%.03f" % 
          (desc,when, 
           gcUsed, gcFree, getOffsetNow()
           ) )

#############################################################################
