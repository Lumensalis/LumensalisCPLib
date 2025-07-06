############################################################################
## INTERNAL USE ONLY

import supervisor, gc, sys

class _MainLoopControl(object):
    
    def __init__(self):
        self.__started = supervisor.ticks_ms()
        self.MINIMUM_LOOP = False
        self.ENABLE_PROFILE = False
        self.nextWaitPeriod = 0.01
        
    def getMsSinceStart(self):
        now = supervisor.ticks_ms()
        if now < self.__started:
            self.__started = now
        return now - self.__started
    
_mlc = _MainLoopControl()

def printElapsed(desc):
    gcUsed = gc.mem_alloc()
    gcFree = gc.mem_free()
    print( "%s : _mlc.getMsSinceStart()=%0.3f | %r used, %r free" % 
          (desc,_mlc.getMsSinceStart()/1000.0, 
           gcUsed, gcFree
           ) )
    
        
class GCManager(object):
    
    def __init__(self):
        self.priorCycle = 0
        self.priorMs = 0
        self.prior_mem_alloc = 0
        self.prior_mem_free = 0
        self.prior_collect_period = None
        self.main = None
        
        self.min_delta_free = 32768
        self.__absoluteMinimumThreshold = 128000
        self.__actualFreeThreshold = 128000
        
        self.freeBuffer = None
        self.targetCollectPeriod = 0.15
        self.minCollectRatio = 0.0035
        
        self.freeAfterLastCollection = gc.mem_free()
        self.PROFILE_MEMORY = False
        self.PROFILE_MEMORY_NESTED = False
        self.PROFILE_MEMORY_ENTRIES = False
        self.SHOW_ZERO_ALLOC_ENTRIES = True
    
    def setFreeThreshold(self, threshold ):
        self.__actualFreeThreshold = max( threshold, self.__absoluteMinimumThreshold )
        
    def setMinimumThreshold(self, threshold ):
        self.__absoluteMinimumThreshold  = threshold
        self.__actualFreeThreshold = max( self.__actualFreeThreshold, self.__absoluteMinimumThreshold )
        
    def runCollection(self, context=None, when=None, force = False, show=False):
        
        mem_free_before = gc.mem_free()
        if mem_free_before > self.__actualFreeThreshold and not force:
            # print( f"GC free = {mem_free_before}" )
            if show:

                mem_alloc_before = gc.mem_alloc()
                timeBeforeCollect = self.main.newNow
                cycle = self.main.cycle
                delta_cycles = max( 1, cycle - self.priorCycle )
                currentMs = _mlc.getMsSinceStart()
                elapsedSincePriorCollectMS = currentMs - self.priorMs
                delta_alloc = mem_alloc_before - self.prior_mem_alloc 
                delta_free = mem_free_before - self.prior_mem_free
                #print( f"cycle {cycle}, {len(main.timers.timers)}")
                elapsedSeconds = elapsedSincePriorCollectMS/1000.0
                print( f"GC per cycle = {elapsedSeconds/delta_cycles:0.03f}s, alloc={delta_alloc/delta_cycles:0.1f}, free={delta_free/delta_cycles:0.1f} skipping at {_mlc.getMsSinceStart()/1000.0:0.3f} / {timeBeforeCollect:0.3f} [{cycle}],  free={mem_free_before} alloc={mem_alloc_before}, since last collect = {elapsedSincePriorCollectMS/1000.0:.3f} [{delta_cycles}] {delta_alloc} alloc, {delta_free} free" )

            return

        mem_alloc_before = gc.mem_alloc()

        sys.stdout.write( "GC collect " )
        
        # run collection
        timeBeforeCollect = self.main.newNow
        gc.collect()
        timeAfterCollect = self.main.newNow
        
        
        
        currentMs = _mlc.getMsSinceStart()
        mem_alloc_after = gc.mem_alloc()
        mem_free_after = gc.mem_free()
        
        # calculate elapsed / deltas
        collectElapsed = timeAfterCollect-timeBeforeCollect
        
        elapsedSincePriorCollectMS = currentMs - self.priorMs
        elapsedSincePriorCollect = elapsedSincePriorCollectMS/1000.0

        cycle = self.main.cycle
        delta_alloc = mem_alloc_before-mem_alloc_after
        delta_free = mem_free_before - mem_free_after 
        delta_cycles = max( 1, cycle - self.priorCycle )
        collectRatio = collectElapsed / elapsedSincePriorCollect
        
        print( f" took {collectElapsed:.3f} of {elapsedSincePriorCollect:.3f} at {_mlc.getMsSinceStart()/1000.0:0.3f} for {delta_cycles} cycles freeing {delta_alloc} ( {delta_alloc/delta_cycles:.1f} per cycle) leaving {mem_alloc_after} used, {mem_free_after} free t={self.__actualFreeThreshold} cr={collectRatio}" )

        if self.targetCollectPeriod is not None and collectElapsed > self.targetCollectPeriod:
            

            newThreshold = self.__actualFreeThreshold
            reason = ""
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
                print( f"  (threshold changing {newThreshold - self.__actualFreeThreshold } from {self.__actualFreeThreshold} to {newThreshold} for {reason} df={delta_free}, cr={collectRatio})")
                self.__actualFreeThreshold = newThreshold


        self.priorMs = currentMs
        self.prior_mem_alloc = mem_alloc_after
        self.prior_mem_free = mem_free_after
        self.priorCycle = cycle
        self.prior_collect_period = collectElapsed
        

        #print( f"cycle {cycle}, {len(main.timers.timers)}")
        #print( f"GC collection at {timeBeforeCollect:0.3f} took {timeAfterCollect-timeBeforeCollect:.3f} of {elapsedSincePriorCollectMS/1000.0:.3f} for {delta_cycles} cycles freeing {delta_alloc} ( {delta_alloc/delta_cycles:.1f} per cycle) leaving {mem_alloc_after} used, {mem_free_after} free" )
            
            
gcm = GCManager()