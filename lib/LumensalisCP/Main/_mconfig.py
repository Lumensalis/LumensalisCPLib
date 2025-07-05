############################################################################
## INTERNAL USE ONLY

import supervisor, gc

class _MainLoopControl(object):
    
    def __init__(self):
        self.__started = supervisor.ticks_ms()
        self.MINIMUM_LOOP = False
        self.ENABLE_PROFILE = False
    
    def getMsSinceStart(self):
        now = supervisor.ticks_ms()
        if now < self.__started:
            self.__started = now
        return now - self.__started
    
_mlc = _MainLoopControl()

def printElapsed(desc):
    gcUsed = gc.mem_alloc()
    gcFree = gc.mem_free()
    print( "%s : _mlc.getMsSinceStart()=%r | %r used, %r free" % 
          (desc,_mlc.getMsSinceStart(), 
           gcUsed, gcFree
           ) )
    
        
class GCManager(object):
    
    def __init__(self):
        self.priorCycle = 0
        self.priorMs = 0
        self.main = None
        self.minimumThreshold = 128000
        self.freeAfterLastCollection = gc.mem_free()
        self.PROFILE_MEMORY = False
        self.PROFILE_MEMORY_NESTED = False
        self.PROFILE_MEMORY_ENTRIES = False
        self.SHOW_ZERO_ALLOC_ENTRIES = True
        
    def runCollection(self, context=None, when=None, force = False):
        
        memFreeBefore = gc.mem_free()
        if memFreeBefore > self.minimumThreshold and not force:
            # print( f"GC free = {memFreeBefore}" )
            return

        memUsedBefore = gc.mem_alloc()
        print( f"GC collecting at {_mlc.getMsSinceStart()}ms, down to {memFreeBefore} free with {memUsedBefore} used" )
        
        start = self.main.newNow
        gc.collect()
        end = self.main.newNow
        memUsedAfter = gc.mem_alloc()
        cycle = self.main.cycle
        cycles = max( 1, cycle - self.priorCycle )
        self.priorCycle = cycle
        freed = memUsedBefore-memUsedAfter
        
        memFreeAfter = gc.mem_free()
        currentMs = _mlc.getMsSinceStart()
        elapsedMs = currentMs - self.priorMs
        self.priorMs = currentMs
        #print( f"cycle {cycle}, {len(main.timers.timers)}")
        print( f"GC collection took {end-start:.3f} of {elapsedMs/1000.0:.3f} for {cycles} cycles freeing {freed} ( {freed/cycles:.1f} per cycle) leaving {memUsedAfter} used, {memFreeAfter} free" )
            
            
gcm = GCManager()