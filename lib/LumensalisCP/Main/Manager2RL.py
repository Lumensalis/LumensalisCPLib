from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler, ImportProfiler
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

from LumensalisCP.Main.Async import MainAsyncChild, ManagerAsync
from LumensalisCP.Main.MainAsyncLoop import MainAsyncLoop

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager

#############################################################################

mlc = pmc_mainLoopControl

_module = ReloadableModule( 'LumensalisCP.Main.Manager' )
_mmMeta = _module.reloadableClassMeta('MainManager', stripPrefix='MainManager_')


@_mmMeta.reloadableMethod()
def _finishInit(self:MainManager) -> None: 

    self.asyncLoop = MainAsyncLoop(main=self)
    #self.asyncLoop.enableDbgOut = True

    def runCollect(context:EvaluationContext) -> None:
        #print( f"pmc_gcManager.runCollection {context.updateIndex}..." )
        pmc_gcManager.checkAndRunCollection(context, show=pmc_gcManager.showRunCollection)

    def getRefreshRate() -> TimeSpanInSeconds:
        """ Get the refresh rate for the collection check interval. """
        return pmc_gcManager.collectionCheckInterval
    

    rCollect = RefreshablePrdInvAct(
        name='runCollect',
        invocable=runCollect,
        autoList=self._refreshables,
        refreshRate=2.3,
        
    )
    self._rrCollect = rCollect
    #rCollect.enableDbgOut = True
    rCollect.activate() 

    def showLoop(context:EvaluationContext) -> None:
        self.infoOut( "cycle %d at %.3f : scene %s ip=%s, gmf=%d cd=%r",
                        self.__cycle, self._when, 
                        self.scenes.currentScene, self._webServer,
                        gc.mem_free(), self.cycleDuration
                )

    rShowLoop = RefreshablePrdInvAct(
        name='ShowLoop',
        invocable=showLoop,
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
