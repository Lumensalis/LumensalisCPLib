from ..DemoCommon import *

from LumensalisCP.Main._mconfig import gcm
from LumensalisCP.Main.Profiler import *
import sys

dumpConfig = ProfileWriteConfig(target=sys.stdout,
        minE = 0.0001,
        minF=0.15,
        minSubF = 0.0001,
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
            
        #print( f"entry {ProfileFrameEntry._allocs}/{ProfileFrameEntry._resets}  | base {ProfileFrameBase._allocs}/{ProfileFrameBase._resets}  ")
        print( f"{fmtPool(ProfileFrameEntry)} {fmtPool(ProfileFrame)} {fmtPool(ProfileSubFrame)} {fmtPool(ProfileFrameBase)}" )
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