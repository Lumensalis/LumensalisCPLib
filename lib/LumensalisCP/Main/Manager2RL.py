from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler, ImportProfiler
__sayImport = getImportProfiler( globals(), reloadable=True )


# pylint: disable=protected-access, bad-indentation, missing-function-docstring
# pylint: disable=no-member, redefined-builtin, unused-argument
# pyright: reportPrivateUsage=false, reportUnusedImport=false, reportUnusedFunction=false

import wifi
import time
import displayio

from LumensalisCP.commonPreManager import *
from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl, pmc_gcManager, sayAtStartup
from LumensalisCP.util.Reloadable import ReloadableModule

from LumensalisCP.Temporal.Refreshable import *
from LumensalisCP.Temporal.RefreshableList import RefreshableListInterface

from LumensalisCP.Main.Async import MainAsyncChild, ManagerAsync
from LumensalisCP.Main.MainAsync import MainAsyncLoop, MainGCLoop
from LumensalisCP.Main import GetManager
from LumensalisCP.Temporal.RefreshableList import RootRefreshableList
from LumensalisCP.Temporal.TimeTracker import TimingTracker

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager

#############################################################################

mlc = pmc_mainLoopControl

_module = ReloadableModule( 'LumensalisCP.Main.Manager' )
_mmMeta = _module.reloadableClassMeta('MainManager', stripPrefix='MainManager_')

@_mmMeta.reloadableMethod()
def __earlyInit(self:MainManager):

        #self.__startNs = getOffsetNow_ns()
        #self.__startNow = getOffsetNow()
        #self.__startNow = TimeInSeconds( getOffsetNow() - pmc_mainLoopControl.getMsSinceStart()/1000.0 )
        #self._when = TimeInSeconds( self.getNewNow() - self.__startNow )
        self._when = getOffsetNow() # self.getNewNow()
        getMainManager.set(self)

        from LumensalisCP.Main.Dependents import MainRef  # pylint: disable=
        MainRef._theManager = self  # type: ignore
        
        self._privateCurrentContext = EvaluationContext(self)
        UpdateContext._patch_fetchCurrentContext(self) # type: ignore
        
        def getCurrentEvaluationContext() -> EvaluationContext:
            return self._privateCurrentContext
        GetManager.getCurrentEvaluationContext = getCurrentEvaluationContext
        sayAtStartup( "context access patched" )
        
        self._refreshables = RootRefreshableList(name='mainRefreshables')
        self.profiler = Profiler(self._privateCurrentContext )
        sayAtStartup(f"profiler created, disabled={self.profiler.disabled}" )

        PreMainConfig.pmc_gcManager.main = self # type: ignore

        self.__cycle = 0

        
        self.asyncManager = ManagerAsync(main=self)
        
        self.__socketPool = None
        
        Debuggable._getNewNow = self.getNewNow # type: ignore

        displayio.release_displays()
        
@_mmMeta.reloadableMethod()
def _showLoop(self:MainManager, context:EvaluationContext) -> None:
    when = context.when
    cycle = context.updateIndex
    try:
        showLoopData = self._showLoopData
    except AttributeError:
        showLoopData:StrAnyDict = {
            'lastCycle': cycle,
            'lastWhen': when,
            'statsBuffer': {}
        }
        self._showLoopData = showLoopData
    
    elapsedTime = when - showLoopData['lastWhen']
    perCycle = elapsedTime / max(1, cycle - showLoopData['lastCycle']) 
    self.infoOut( "cycle %d at %.3f : %.3f %r : scene %s ip=%s, gmf=%d",
                    self.asyncLoop.cycle, self._when, 
                    perCycle,
                    self.asyncLoop.tracker.stats(showLoopData['statsBuffer']),
                    self.scenes.currentScene, self._webServer,
                    gc.mem_free()
            )
    showLoopData['lastCycle'] = self.asyncLoop.cycle
    showLoopData['lastWhen'] = self._when

@_mmMeta.reloadableMethod()
def _finishInit(self:MainManager) -> None: 

    self.asyncLoop = MainAsyncLoop(main=self)
    #self.asyncLoop.enableDbgOut = True
    self.gcLoop = MainGCLoop(main=self)

    def callShowLoop(context:EvaluationContext) -> None:
        self._showLoop(context)

    rShowLoop = RefreshablePrdInvAct(
        name='ShowLoop',
        invocable=callShowLoop,
        autoList=self._refreshables,
        refreshRate=10.0,
        
    )
    #rShowLoop.enableDbgOut = True
    rShowLoop.activate() 
    #self._rrShowLoop = rShowLoop

    def runDeferred(context:EvaluationContext) -> None:
        self.runDeferredTasks(context)
        if len(self.__deferredTasks) == 0:
            assert self._rrDeferred is not None, "rrDeferred should not be None"
            self._rrDeferred.deactivate(context)

    rDeferred = RefreshablePrdInvAct(
        name='rDeferred',
        invocable=runDeferred,
        autoList=self._refreshables,
        refreshRate=2.3,
        
    )
    self._rrDeferred = rDeferred
    #rCollect.enableDbgOut = True
    rDeferred.activate() 



@_mmMeta.reloadableMethod()
def addBasicWebServer( self:MainManager, *args:Any, **kwds:StrAnyDict ):
    self.sayAtStartup( "addBasicWebServer %r, %r ", args, kwds )
    from LumensalisCP.HTTP.BasicServer import BasicServer
    ImportProfiler.dumpWorstImports(10)
    

    #self.__asyncTaskCreators.append( server.createAsyncTasks )
    
    def startWebServer():
        self.sayAtStartup( "startWebServer"  )
        socket = self.socketPool
        self.sayAtStartup( "socketPool=%r", socket )

        server = BasicServer( *args, main=self, **kwds )
        self._webServer = server
        self.sayAtStartup( f"self._webServer = {self._webServer}" )
        if False:

            if wifi.radio.ipv4_address is not None:
                address = str(wifi.radio.ipv4_address)

                self.sayAtStartup( "startWebServer on %r ", address )
                server = BasicServer( *args, main=self, **kwds )
                self._webServer = server
                self._webServer.start(address) # type: ignore

            else:
                self.sayAtStartup( "no address for startWebServer" )
    self.callLater( startWebServer )



__sayImport.complete(globals())
