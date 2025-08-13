from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler
__sayImport = getImportProfiler( globals(), reloadable=True )

# pylint: disable=protected-access, bad-indentation, missing-function-docstring
# pylint: disable=no-member, redefined-builtin, unused-argument
# pyright: reportPrivateUsage=false, reportUnusedImport=false, reportUnusedFunction=false

from LumensalisCP.commonPreManager import *
from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl, pmc_gcManager
from LumensalisCP.Temporal.TimeTracker import TimingTracker

from LumensalisCP.Main.Async import MainAsyncChild
from LumensalisCP.util.Reloadable import addReloadableClass
from LumensalisCP.Main import MainAsyncRL

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager

#############################################################################
mlc = pmc_mainLoopControl

class MainGCLoop(MainAsyncChild):
    DEFAULT_loopSleepDuration:TimeInMS = 1000

    async def runAsyncSetup(self) -> None:
        self.gcSleepMS = 1000

    async def runAsyncSingleLoop(self, when:TimeInSeconds) -> None:
        raise NotImplementedError

class MainAsyncLoop(MainAsyncChild):
    
    def __init__(self, **kwds:Unpack[MainAsyncChild.KWDS]):
        kwds.setdefault('loopSleepDuration', 0)
        super().__init__(**kwds)
        self.latestSleepDuration:float = 0.0
        self.cycle:int = 0
        self.priorSleepWhen:float = 0.0
        #self.nextWait:float = 0.0
        self.innerTracker:TimingTracker = TimingTracker()
        self.loopMode:int = 0

    async def runAsyncSetup(self) -> None:
        main = self.main
        self.priorSleepWhen = main.getNewNow()
        self.startupOut( "pre-run gc..." )
        pmc_gcManager.checkAndRunCollection(force=True)
        self.startupOut( "starting manager main run" )
        self.priorSleepWhen = main.getNewNow()
        #self.nextWait = main.getNewNow()
        main._when = self.priorSleepWhen
        self._step = 0

    async def runAsyncSingleLoop(self, when:TimeInSeconds) -> None:
        raise NotImplementedError

    def asyncTaskStats(self, out:Optional[dict[str,Any]]=None) -> dict[str,Any]:
        raise NotImplementedError

#############################################################################
addReloadableClass( MainAsyncLoop, MainAsyncRL )
addReloadableClass( MainGCLoop, MainAsyncRL )


__sayImport.complete()
