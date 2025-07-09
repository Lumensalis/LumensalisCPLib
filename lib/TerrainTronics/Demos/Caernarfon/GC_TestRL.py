from LumensalisCP.Main._preMainConfig import _mlc,gcm,printElapsed
printElapsed("starting import GCTest_RL")

from LumensalisCP.Main._preMainConfig import *
from ..DemoCommon import *
from LumensalisCP.Main.Profiler import *
import gc, supervisor, sys
from LumensalisCP.util.importing import reload

printElapsed("import GCTest_RL internal")
dumpConfig = ProfileWriteConfig(target=sys.stdout,
        minE = 0.000,
        minF=0.015,
        minSubF = 0.005,
        minB = 0,
    )

printDumpInterval = 21
collectionCheckInterval = 3.51
usbCheckInterval = 0.25


def setupMlcAndGcm():
    _mlc.ENABLE_PROFILE = True
    gcm.PROFILE_MEMORY = True
    gcm.PROFILE_MEMORY_NESTED = True
    gcm.PROFILE_MEMORY_ENTRIES = True
    


import gc

def reloadSelf():
    from . import GC_TestRL
    from LumensalisCP.Main import ProfilerRL
    reload( ProfilerRL )
    reload( GC_TestRL )
    
def usbCheck(  context:UpdateContext, when:TimeInSeconds|None=None ):
    available = supervisor.runtime.serial_bytes_available
    if available:
        print( f"stdin available = {available}...")
        incoming = sys.stdin.read(available)
        print( f"stdin incoming = {repr(incoming)}")
        if incoming == "R":
            reloadSelf()
        elif incoming == "A":
            ar = not supervisor.runtime.autoreload 
            print( f"setting supervisor.runtime.autoreload = {ar}")
            supervisor.runtime.autoreload = ar
        elif incoming == "B":
            supervisor.reload()
        elif incoming == "s":
            ar = supervisor.runtime.autoreload 
            print( f"supervisor.runtime.autoreload = {ar}")


def runCollection( context:UpdateContext, when:TimeInSeconds|None=None,
                  force:bool=False, show:bool=False):

    usbCheck( context, when )
    gcm.runCollection(context,when, force=force, show=show)

def fmtPool( cls ):
    pool = cls.getReleasablePool()
    return f"[{cls.__name__} a:{pool._allocs} r:{pool._releases}]"
    
def printDump( main:MainManager ):
    
    context = main.getContext()
    i = context.updateIndex
    
    count = 10
    framesFound = 0
    while count and i >= 0:
        count -= 1
        frame = main.profiler.timingForUpdate( i )
        
        if frame is not None:
            framesFound += 1
            frame.writeOn( dumpConfig )
        i -= 1

    #print( f"entry {ProfileSnapEntry._allocs}/{ProfileSnapEntry._resets}  | base {ProfileFrameBase._allocs}/{ProfileFrameBase._resets}  ")
    print( f"pools : {fmtPool(ProfileSnapEntry)} {fmtPool(ProfileFrame)} {fmtPool(ProfileSubFrame)} {fmtPool(ProfileFrameBase)}" )
    print( f"   gc.mem_alloc={gc.mem_alloc()} gc.mem_free={gc.mem_free()}" )
    gcm.runCollection(context, force=True )
        
printElapsed("import GCTest_RL complete")
        