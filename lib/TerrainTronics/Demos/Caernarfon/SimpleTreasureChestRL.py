from LumensalisCP.Demo.DemoCommon import *

from LumensalisCP.Main.PreMainConfig import pmc_gcManager, pmc_mainLoopControl
from LumensalisCP.Main.Profiler import *
import sys
import LumensalisCP.pyCp.importlib

from LumensalisCP.Triggers.Timer import PeriodicTimer, addPeriodicTaskDef

from . import SimpleTreasureChest
import wifi

printDumpInterval = 33
collectionCheckInterval = 5.51
pmc_mainLoopControl.ENABLE_PROFILE = False
#gcm.setMinimumThreshold(1638400)
pmc_gcManager.setMinimumThreshold(638400)
dumpConfig = ProfileWriteConfig(target=sys.stdout,
        minE = 0.000,
        minF=0.015,
        minSubF = 0.005,
        minB = 0,
    )

def reloadSimpleTreasureChestRL():
    from . import SimpleTreasureChestRL
    LumensalisCP.pyCp.importlib.reload( SimpleTreasureChestRL )
    
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
    
    if pmc_mainLoopControl.ENABLE_PROFILE :
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
    print( f"   {main.cycle} {main.scenes.currentScene.name} gc.mem_free={gc.mem_free()}  ip={wifi.radio.addresses}" )
        #gcm.runCollection(context, force=True )
        
def TreasureChest_finishSetup(self:SimpleTreasureChest.TreasureChest):
    main = self.main
    from . import SimpleTreasureChestRL
    @addPeriodicTaskDef( "gc-collect", period=lambda: SimpleTreasureChestRL.collectionCheckInterval, main=main )
    def runCollection(context=None, when=None):
        pmc_gcManager.runCollection(context,when, show=False)

    def firstGC():
        pmc_gcManager.runCollection(main.getContext(),main.when, force=True)
    main.callLater(firstGC)
    main.scenes.enableDbgOut = True

    dt = PeriodicTimer( interval=lambda : SimpleTreasureChestRL.printDumpInterval, manager=main.timers, name="dump" )
    @dt.addTaskDef( )
    def  printDump():
        SimpleTreasureChestRL.printDump(main)

                
    gc.disable()