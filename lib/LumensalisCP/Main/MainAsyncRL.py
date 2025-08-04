from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler
__sayMALRLImport = getImportProfiler( globals(), reloadable=True )

# pylint: disable=protected-access, bad-indentation, missing-function-docstring
# pylint: disable=no-member, redefined-builtin, unused-argument
# pyright: reportPrivateUsage=false, reportUnusedImport=false, reportUnusedFunction=false
# pyright: reportRedeclaration=false

from LumensalisCP.commonPreManager import *
from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl, pmc_gcManager

from LumensalisCP.util.Reloadable import ReloadableModule
from LumensalisCP.Main.Async import MainAsyncChild

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    from LumensalisCP.Main.MainAsync import MainAsyncLoop, MainGCLoop

#############################################################################
mlc = pmc_mainLoopControl

_module = ReloadableModule( 'LumensalisCP.Main.MainAsync' )
_MainGCLoop = _module.reloadableClassMeta( 'MainGCLoop' )
_MainAsyncLoop = _module.reloadableClassMeta( 'MainAsyncLoop' )

@_MainGCLoop.reloadableMethod()
async def runAsyncSingleLoop(self:MainGCLoop, when:TimeInSeconds) -> None:
    pmc_gcManager.checkAndRunCollection( force=False, show=False )


@_MainAsyncLoop.reloadableMethod()
def asyncTaskStats(self:MainAsyncLoop, out:Optional[dict[str,Any]]=None) -> dict[str,Any]:
    rv = MainAsyncChild.asyncTaskStats(self,out)
    #rv = super(self).asyncTaskStats(out)
    rv['latestSleepDuration'] = self.latestSleepDuration
    rv['cycle'] = self.cycle
    rv['priorSleepWhen'] = self.priorSleepWhen
    rv['loopMode'] = self.loopMode
    #rv['nextWait'] = self.nextWait
    return rv

@_MainAsyncLoop.reloadableMethod()
async def runAsyncSingleLoop(self:MainAsyncLoop, when:TimeInSeconds) -> None:
    if self.loopMode == 99: return
    try:
        main = self.main
        now = self.innerTracker.start()
        
        self._step += 1
        if self.loopMode < 5:
            with main.getNextFrame(now): #  as activeFrame:
                context = main._privateCurrentContext
                if self.loopMode < 3:
                    if self._step == 1:
                        main._refreshables.process(context, context.when)
                    elif self._step == 2:
                        main._timers.update( context )
                    elif self._step == 3:
                        main._scenes.run(context)
                    else:
                        self._step = 0

        if self.loopMode < 10:
            self.cycle += 1
            self.priorSleepWhen = self.innerTracker.stop()


    except Exception as inst:
        print( "Exception in MainAsyncLoop.runAsyncSingleLoop: " + safeRepr(inst) )
        self.SHOW_EXCEPTION(inst, "error in MainAsyncLoop.runAsyncSingleLoop")
        raise

__sayMALRLImport.complete()