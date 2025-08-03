from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler
__sayImport = getImportProfiler( globals(), reloadable=True )


# pylint: disable=protected-access, bad-indentation, missing-function-docstring
# pylint: disable=no-member, redefined-builtin, unused-argument
# pyright: reportPrivateUsage=false, reportUnusedImport=false, reportUnusedFunction=false

import wifi

from LumensalisCP.commonPreManager import *
from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl #, pmc_gcManager
from LumensalisCP.util.Reloadable import ReloadableModule

from LumensalisCP.Temporal.Refreshable import *
from LumensalisCP.Temporal.RefreshableList import RefreshableListInterface

from .Async import MainAsyncChild, ManagerAsync

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager

#############################################################################
mlc = pmc_mainLoopControl

class MainAsyncLoop(MainAsyncChild):

    def __init__(self, **kwds:Unpack[MainAsyncChild.KWDS]):
        super().__init__(**kwds)
        self.latestSleepDuration:float = 0.0
        self.cycle:int = 0
        self.priorSleepWhen:float = 0.0
        self.nextWait:float = 0.0

    def asyncTaskStats(self, out:Optional[dict[str,Any]]=None) -> dict[str,Any]:
        rv = super().asyncTaskStats(out)
        rv['latestSleepDuration'] = self.latestSleepDuration
        rv['cycle'] = self.cycle
        rv['priorSleepWhen'] = self.priorSleepWhen
        rv['nextWait'] = self.nextWait
        return rv

    async def runAsyncSetup(self) -> None:
        main = self.main
        self.priorSleepWhen = main.getNewNow()
        self.startupOut( "pre-run gc..." )
        pmc_gcManager.checkAndRunCollection(force=True)
        self.startupOut( "starting manager main run" )
        self.priorSleepWhen = main.getNewNow()
        self.nextWait = main.getNewNow()
        main._when = self.nextWait
        
    async def runAsyncSingleLoop(self) -> None:
        try:
            main = self.main
            with main.getNextFrame(): #  as activeFrame:
                context = main._privateCurrentContext

                main._refreshables.process(context, context.when)
                main._timers.update( context )
                main._scenes.run(context)
                main.cycleDuration = 1.0 / (main.cyclesPerSecond *1.0)
                self.priorSleepWhen = main.getNewNow()
                self.nextWait += mlc.nextWaitPeriod # type: ignore
        except Exception as inst:
            print( "Exception in MainAsyncLoop.runAsyncSingleLoop: " + safeRepr(inst) )
            self.SHOW_EXCEPTION(inst, "error in MainAsyncLoop.runAsyncSingleLoop")
            raise

#############################################################################

__sayImport.complete()
