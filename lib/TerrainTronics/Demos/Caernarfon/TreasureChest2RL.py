from ..DemoCommon import *

import sys

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
        
def printDump( main:MainManager ):
    
    if True:
        i = main.getContext().updateIndex
        
        count = 50
        minE = 0.01
        minF=0.05
        
        while count and i >= 0:
            count -= 1
            frame = main.profiler.timingForUpdate( i )
            
            if frame is not None:
                frame.writeOn( sys.stdout, minE = minE, minF = minF )
            i -= 1
        #return rv
    else:
        timings = main.dumpLoopTimings(50, minE = 0.01, minF=0.035)
        print( "----" )
        for frame in timings:
            printFrame(frame)
        print( "----" )
        #print( f"{timings}" )
        #print( json.dumps( timings ) )