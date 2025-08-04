import sys
# pylint: disable=unused-import,protected-access,redefined-outer-name,unused-variable 
# pylint: disable=import-self, no-member,unused-argument
# pylint: disable=undefined-variable, import-outside-toplevel
# type: ignore=reportOptionalMemberAccess,reportAttributeAccess
# pyright: reportOptionalMemberAccess=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportUndefinedVariable=false

from LumensalisCP.Demo.DemoCommon import *
from LumensalisCP.Main.PreMainConfig import pmc_gcManager, pmc_mainLoopControl
from LumensalisCP.Main.Profiler import *
import LumensalisCP.pyCp.importlib

#from LumensalisCP.Triggers.Timer import PeriodicTimer, addPeriodicTaskDef

from TerrainTronics.Demos.Caernarfon import SimpleTreasureChest

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
    return f"[{cls.__name__} a:{pool._allocs} r:{pool._releases}]"


def TreasureChest_finishSetup(self:SimpleTreasureChest.TreasureChest):
    if False:
        main = self.main
        from . import SimpleTreasureChestRL
        @addPeriodicTaskDef( "gc-collect", period=lambda: pmc_gcManager.collectionCheckInterval, main=main )
        def runCollection(context=None, when=None):
            pmc_gcManager.runCollection(context,when, show=False)

        def firstGC():
            pmc_gcManager.runCollection(main.getContext(),main.when, force=True)
        main.callLater(firstGC)
        main.scenes.enableDbgOut = True

        dt = PeriodicTimer( interval=lambda : SimpleTreasureChestRL.printDumpInterval, manager=main.timers, name="dump" )
        @dt.addSimpleTaskDef( )
        def  printDump():
            SimpleTreasureChestRL.printDump(main)

                
    gc.disable()
