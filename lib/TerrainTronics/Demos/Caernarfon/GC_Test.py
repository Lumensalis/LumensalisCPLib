import LumensalisCP.Main._mconfig, gc

mlc = LumensalisCP.Main._mconfig._mlc
mlc.MINIMUM_LOOP = True
#mlc.MINIMUM_LOOP = False
mlc.ENABLE_PROFILE = False

def printElapsed(desc):
    gcUsed = gc.mem_alloc()
    gcFree = gc.mem_free()
    print( "%s : mlc.getMsSinceStart()=%r | %r used, %r free" % 
          (desc,mlc.getMsSinceStart(), 
           gcUsed, gcFree
           ) )

printElapsed("starting imports")


from ..DemoBase import DemoBase
from LumensalisCP.Triggers.Timer import PeriodicTimer, addPeriodicTaskDef
from LumensalisCP.util.bags import Bag

import gc

printElapsed("parsing class GC_Test")

class GC_Test( DemoBase ):

    def setup(self):
        main = self.main
        rcData = Bag(
            priorCycle = main.cycle,
            priorMs = mlc.getMsSinceStart(),
        )
        @addPeriodicTaskDef( "gc-collect", period=0.5, main=main )
        def runCollection(context=None, when=None):
            memBefore = gc.mem_alloc()
            start = main.newNow
            gc.collect()
            end = main.newNow
            memAfter = gc.mem_alloc()
            cycle = main.cycle
            cycles = max( 1, cycle - rcData.priorCycle )
            rcData.priorCycle = cycle
            freed = memBefore-memAfter
            currentMs = mlc.getMsSinceStart()
            elapsedMs = currentMs - rcData.priorMs
            rcData.priorMs = currentMs
            #print( f"cycle {cycle}, {len(main.timers.timers)}")
            print( f"GC collection took {end-start:.3f} of {elapsedMs/1000.0:.3f} for {cycles} cycles freeing {freed} ( {freed/cycles:.1f} per cycle) leaving {memAfter}" )
            
        gc.disable()
    
def demoMain(*args,**kwds):
    printElapsed("instantiating GC_Test")
    demo = GC_Test( *args, **kwds )
    
    printElapsed("calling demo.run()")
    demo.run()