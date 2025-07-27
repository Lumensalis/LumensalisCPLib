#from LumensalisCP.Demo.DemoCommon import *

#from LumensalisCP.Main.PreMainConfig import pmc_gcManager
from LumensalisCP.Main.Profiler import *
import sys

printDumpInterval = 21
collectionCheckInterval = 3.51

dumpConfig = ProfileWriteConfig(target=sys.stdout,
        minE = 0.000,
        minF=0.015,
        minSubF = 0.005,
        minB = 0,
    )

def printEntry( name, entry, indent='' ):
    data = dict(**entry)
    lw = data.pop('lw')
    e = data.pop('e')
    nest = data.pop('nest',None)
    print(f"{indent}{e:0.3f} {lw:0.3f} {name:32s} {data}")
    if nest is not None:
        printFrame( nest, indent+"  ")   


def printFrame( frame, indent='' ):
    #print( f"{frame}" )
    data = dict(**frame)
    i = data.pop('i')
    e = data.pop('e')
    #eSleep = data.pop('eSleep',None)
    entries = data.pop('entries')
    print(f"{indent}{e:0.3f} [{i}] {data}")
    indent = indent + "  "
    for name, entry in entries.items():
        printEntry(name, entry, indent )



def fmtPool( cls ):
    pool = cls.getReleasablePool()
    return f"[{cls.__name__} a:{pool._allocs} r:{pool._releases}]"
def printDump( main:MainManager ):
    
    if True:
        context = main.getContext()
        i = context.updateIndex
        
        count = 10
        while count and i >= 0:
            count -= 1
            frame = main.profiler.timingForUpdate( i )
            
            if frame is not None:
                frame.writeOn( dumpConfig )
            i -= 1
            
        #print( f"entry {ProfileSnapEntry._allocs}/{ProfileSnapEntry._resets}  | base {ProfileFrameBase._allocs}/{ProfileFrameBase._resets}  ")
        print( f"{fmtPool(ProfileSnapEntry)} {fmtPool(ProfileFrame)} {fmtPool(ProfileSubFrame)} {fmtPool(ProfileFrameBase)}" )
        print( f"   gc.mem_alloc={gc.mem_alloc()} gc.mem_free={gc.mem_free()}" )
        #gcm.runCollection(context, force=True )
    else:
        timings = main.dumpLoopTimings(50, minE = 0.01, minF=0.035)
        print( "----" )
        for frame in timings:
            printFrame(frame)
        print( "----" )
        #print( f"{timings}" )
        #print( json.dumps( timings ) )