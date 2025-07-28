

from LumensalisCP.Main.PreMainConfig import ReloadableImportProfiler
__saySimpleProfilingRLImport = ReloadableImportProfiler( "Simple.profilingRL" )


#from LumensalisCP.Demo.DemoCommon import *

#from LumensalisCP.Main.PreMainConfig import pmc_gcManager
from LumensalisCP.Main.Profiler import *
import sys

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    from LumensalisCP.Main.Profiler import ProfileSnapEntry, ProfileFrame, ProfileSubFrame, ProfileFrameBase, ProfileWriteConfig

printDumpInterval = 21
collectionCheckInterval = 3.51

dumpConfig = ProfileWriteConfig(target=sys.stdout,
        minE = 0.000,
        minF=0.015,
        minSubF = 0.005,
        minB = 0,
    )

def addPoolInfo( dest:StrAnyDict,  cls:type[ProfileSnapEntry|ProfileFrame|ProfileSubFrame|ProfileFrameBase]) -> Any:
    pool = cls.getReleasablePool()
    return dictAddUnique(dest, cls.__name__, dict( a=pool._allocs, r=pool._releases ) )

def getProfilerInfo( main:MainManager ) -> Any:
    
    if True:
        context = main.getContext()
        i = context.updateIndex
        rv:StrAnyDict = {}
        dumpConfig = ProfileWriteConfig(target=rv,
                minE = 0.000,
                minF=0.015,
                minSubF = 0.005,
                minB = 0,
            )

        with dumpConfig.nestDict('timers'):
            d = dumpConfig.topDict
            d['timerSorts'] = main.timers.timerSorts
            d['timerChanges'] = [ dict(
                name=timer.name,
                running=timer.running,
                nextFire=timer.nextFire,    
                lastFire=timer.lastFire,
                
            )
                for timer in main.timers.timers]
            
        count = 10
        
        with dumpConfig.nestList('frames'):
            
            while count and i >= 0:
                count -= 1
                frame = main.profiler.timingForUpdate( i )
                
                if frame is not None:
                    with dumpConfig.nestDict():
                        frame.writeOn( dumpConfig )
                i -= 1
        with dumpConfig.nestDict('pools'):
            d = dumpConfig.topDict
            addPoolInfo( d, ProfileSnapEntry )
            addPoolInfo( d, ProfileFrame )
            addPoolInfo( d, ProfileSubFrame )
            addPoolInfo( d, ProfileFrameBase )

        with dumpConfig.nestDict('gc'):
            d = dumpConfig.topDict
            d['mem_alloc'] = gc.mem_alloc()
            d['mem_free'] = gc.mem_free()



        
        return rv
    else:
        timings = main.dumpLoopTimings(50, minE = 0.01, minF=0.035)
        print( "----" )
        for frame in timings:
            printFrame(frame)
        print( "----" )
        #print( f"{timings}" )
        #print( json.dumps( timings ) )

__saySimpleProfilingRLImport.complete()
