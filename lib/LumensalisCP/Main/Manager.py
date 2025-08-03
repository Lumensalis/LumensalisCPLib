from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayMainImport = getImportProfiler( "Main.Manager", globals() )

# pyright: reportUnusedImport=false

import wifi, displayio

import LumensalisCP.Main.Dependents
from LumensalisCP.commonPreManager import *
from LumensalisCP.Main import PreMainConfig
from TerrainTronics.Factory import TerrainTronicsFactory
from LumensalisCP.Shields.Base import ShieldBase
from LumensalisCP.Main.I2CProvider import I2CProvider
from LumensalisCP.Main.Panel import ControlPanel
from LumensalisCP.Temporal.Refreshable import Refreshable
from LumensalisCP.Temporal.RefreshableList import RootRefreshableList
from LumensalisCP.util.Reloadable import addReloadableClass, reloadingMethod

from LumensalisCP.Temporal.Refreshable import *

from LumensalisCP.Main import ManagerRL
from LumensalisCP.Main import Manager2RL
from .Async import ManagerAsync

from . import GetManager

if TYPE_CHECKING:
    from LumensalisCP.Lights.DMXManager import DMXManager
    import LumensalisCP.Main.Manager
    from LumensalisCP.Audio import Audio
    from LumensalisCP.Main.Profiler import Profiler, ProfileFrameBase
    from LumensalisCP.Main.MainAsyncLoop import MainAsyncLoop
    from LumensalisCP.HTTP.BasicServer import BasicServer

    
    # from LumensalisCP.Controllers.Config import ControllerConfigArg

import LumensalisCP.Main.ProfilerRL

_sayMainImport.parsing()

LumensalisCP.Main.ProfilerRL._rl_setFixedOverheads() # type: ignore

def _early_collect(tag:str):
    PreMainConfig.pmc_gcManager.checkAndRunCollection(force=True)

class MainManager(NamedLocalIdentifiable, ConfigurableBase, I2CProvider):
    
    class KWDS(ConfigurableBase.KWDS): # type: ignore
        pass
    
    theManager : MainManager|None = None
    ENABLE_EEPROM_IDENTITY = False
    profiler: Profiler
    shields:NliList[ShieldBase]
    controlPanels:NliList[ControlPanel]
    _privateCurrentContext:EvaluationContext
    asyncLoop:MainAsyncLoop
    
    useWifi:bool

    @staticmethod
    def initOrGetManager() -> "MainManager":
        rv = MainManager.theManager
        if rv is None:
            rv = MainManager()
            assert MainManager.theManager is rv
        return rv

    @staticmethod
    def getManager() -> "MainManager":
        rv = MainManager.theManager
        assert rv is not None
        return rv

    def __init__(self, **kwds:Unpack[ConfigurableBase.KWDS] ) -> None:
        assert MainManager.theManager is None
        NamedLocalIdentifiable.__init__(self,"main")
        
        MainManager.theManager = self
        PreMainConfig.pmc_gcManager.main = self # type: ignore

        self.__cycle = 0
        

        #self.__startNs = time.monotonic_ns()
        #self.__startNow = time.monotonic()
        self.__startNow = time.monotonic() - pmc_mainLoopControl.getMsSinceStart()/1000.0
        self._when:TimeInSeconds = self.getNewNow()
        getMainManager.set(self)

        from LumensalisCP.Main.Dependents import MainRef  # pylint: disable=
        MainRef._theManager = self  # type: ignore
        
        self._privateCurrentContext = EvaluationContext(self)
        UpdateContext._patch_fetchCurrentContext(self) # type: ignore
        
        def getCurrentEvaluationContext() -> EvaluationContext:
            return self._privateCurrentContext
        GetManager.getCurrentEvaluationContext = getCurrentEvaluationContext
        
        self._refreshables = RootRefreshableList(name='mainRefreshables')
        self.profiler = Profiler(self._privateCurrentContext )

        self.asyncManager:ManagerAsync = ManagerAsync(main=self)
        
        self.__socketPool:Any = None
        
        Debuggable._getNewNow = self.getNewNow # type: ignore
        mainConfigDefaults = dict(
            TTCP_HOSTNAME = os.getenv("TTCP_HOSTNAME")
        )
        displayio.release_displays()
        
        kwds.setdefault("defaults", mainConfigDefaults)
        ConfigurableBase.__init__(self, **kwds ) # type: ignore

        
        _early_collect("mid manager init")

        I2CProvider.__init__( self, config=self.config, main=self )
  
        self.__identity = ControllerIdentity(self)
        self._when = self.newNow
        
        self.cyclesPerSecond = 100
        self.cycleDuration = 0.01

        self._webServer:BasicServer|None = None

        self._rrDeferred:RefreshablePrdInvAct|None = None
        self._rrCollect:RefreshablePrdInvAct|None = None

        self.__deferredTasks: collections.deque[Callable[[], None]] = collections.deque( [], 99, True ) # type: ignore # pylint: disable=all
        self.__audio = None
        self.__dmx :DMXManager|None = None

        #self._tasks:List[KWCallback] = []
        self.__shutdownTasks:List[ExitTask] = []
        self.shields = NliList(name='shields',parent=self)


        self.__anonInputs:NliList[InputSource] = NliList(name='inputs',parent=self)
        self.__anonOutputs:NliList[NamedOutputTarget] = NliList(name='outputs',parent=self)
        self.controlPanels = NliList(name='controllers',parent=self)
        self.defaultController = ControlPanel(main=self)
        self.defaultController.nliSetContainer(self.controlPanels)

        self._monitored:list[InputSource] = []

        self._timers = PeriodicTimerManager(main=self)

        self._scenes: SceneManager = SceneManager(main=self)
        self.__TerrainTronics = None

        self._finishInit()


        if pmc_mainLoopControl.preMainVerbose: print( f"MainManager options = {self.config.options}" )
        _early_collect("end manager init")
    
    def makeRef(self):
        return LumensalisCP.Main.Dependents.MainRef(self)

    @property
    def refreshables(self) -> RootRefreshableList:
        """ The root refreshable list for the main manager. """
        return self._refreshables

    @property
    def identity(self) -> ControllerIdentity: return self.__identity

    @property
    def TerrainTronics(self:'MainManager') -> TerrainTronicsFactory:
        """ factory for adding TerrainTronics Castle boards"""
        if self.__TerrainTronics is None:
            from TerrainTronics.Factory import TerrainTronicsFactory
            self.__TerrainTronics = TerrainTronicsFactory( main=self )
        return self.__TerrainTronics
    
    @property
    def when(self) -> TimeInSeconds:
        return self._when 
    
    @property
    def cycle(self) -> int : return self.__cycle 
    @property
    def millis(self) -> TimeInMS : return int(self._when * 1000)
    @property
    def seconds(self) -> TimeInSeconds: return self._when 
    
    def getNewNow( self ) -> TimeInSeconds:
        #ns = time.monotonic_ns()
        #return (ns - self.__startNs) * 0.000000001
        now = time.monotonic()
        return now - self.__startNow # type: ignore # pylint: disable=all


    @property
    def newNow( self ) -> TimeInSeconds: return self.getNewNow()

    @property
    def scenes(self) -> SceneManager: return self._scenes
    
    @property
    def timers(self) -> PeriodicTimerManager: return self._timers
    
    @property
    def latestContext(self)->EvaluationContext: return  self._privateCurrentContext

    def getContext(self)->EvaluationContext: 
        return  self._privateCurrentContext

    @property
    def panel(self) -> ControlPanel:
        """ the default control panel """
        return self.defaultController
    
    @property
    def dmx(self):
        if self.__dmx is None:
            import LumensalisCP.Lights.DMXManager
            self.__dmx = LumensalisCP.Lights.DMXManager.DMXManager( main=self )
 
        return self.__dmx
    
    @property
    def socketPool(self) -> Any:
        if self.__socketPool is None:
            self.sayAtStartup( "socketPool is None, creating it" )
            import adafruit_connection_manager # type: ignore
            if not wifi.radio.connected:
                try:
                    ssid =  os.getenv("LCPF_WIFI_SSID") or os.getenv("CIRCUITPY_WIFI_SSID")
                    password = os.getenv("LCPF_WIFI_PASSWORD") or os.getenv("CIRCUITPY_WIFI_PASSWORD")
                    channel = os.getenv("LCPF_WIFI_CHANNEL")
                    options:dict[str,Any] = {}
                    if channel is not None:
                        options['channel'] = int(channel)
                    self.sayAtStartup(f"Connecting to {ssid!r} with options {options!r}")
                    options.setdefault('password', password)
                    wifi.radio.connect(ssid=ssid, **options) # type: ignore

                    self.sayAtStartup("Connected to %r", ssid)
                except Exception as e:
                    self.sayAtStartup("Failed to connect to WiFi: %s", e)
                    raise
            #import socketpool
            #self.__socketPool = socketpool.SocketPool(wifi.radio)
            #self.sayAtStartup( "wifi.radio.start_dhcp()" )
            #wifi.radio.start_dhcp()
            self.sayAtStartup( "get_radio_socketpool" )
            pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio) # type: ignore
            self.sayAtStartup( "socketPool = %r", pool )
            self.__socketPool = pool
            
        return self.__socketPool # type: ignore
        
    def callLater( self, task:KWCallbackArg ) -> None:
        self.__deferredTasks.append( KWCallback.make( task ) )
        assert self._rrDeferred is not None
        if not self._rrDeferred.isActiveRefreshable:
            self._rrDeferred.activate(self.getContext())

    def __runExitTasks(self):
        print( "running Main exit tasks" )
        for task in self.__shutdownTasks:
            task.shutdown()
            
    def addExitTask(self,task:ExitTask|Callable[[], None]|KWCallbackArg):
        if not isinstance( task, ExitTask ):
            task = ExitTask( main=self,task=task)
            
        self.__shutdownTasks.append(task)

    def addScene( self, **kwds:Unpack[Scene.KWDS] ) -> Scene:
        """ add a new scene - see http://lumensalis.com/ql/h2Scenes

        ```python
scene = main.addScene( )
```
    :param kwds: Keyword arguments for the scene.
    :return: The newly created scene.

        
"""
        scene = self._scenes.addScene( **kwds )
        return scene

    def addScenes( self, n:int ):
        """ add multiple scenes to the manager.
        :param n: The number of scenes to add.
```python
act1, intermission, act2 = main.addScenes(3)
```
see also :meth:`addScene` for adding a single scene.
see http://lumensalis.com/ql/h2Scenes
"""
        #->  Unpack[Tuple[Scene, ...]]:
        return [self.addScene() for _ in range(n)]
        return [self.addScene(name) for name in names]
    
    def sayAtStartup( self, fmt:str, *args:Any ):
        pmc_mainLoopControl.sayAtStartup( fmt, *args)
            #print( "-----" )
            #print( f"{self.getNewNow():0.3f} STARTUP : {safeFmt(fmt,*args)}" )

    @reloadingMethod            
    def addBasicWebServer( self, *args:Any, **kwds:StrAnyDict ) -> None: ...
  
    @reloadingMethod
    def monitor( self, *inputs:InputSource, **kwds:StrAnyDict ) -> None: ...

    @reloadingMethod
    def handleWsChanges( self, changes:StrAnyDict ): ...
     
    #async def msDelay( self, milliseconds:TimeInMS ):
    #    await asyncio.sleep( milliseconds * 0.001 )
    
    @property
    def audio(self) -> Audio:
        if self.__audio is None:
            self.addI2SAudio()
            assert self.__audio is not None
        return self.__audio

    def addI2SAudio(self, *args:Any, **kwds:Unpack[Audio.KWDS] ) -> Audio:
        from LumensalisCP.Audio import Audio
        assert self.__audio is None
        kwds.setdefault('main', self )
        self.__audio = Audio( **kwds )
        return self.__audio

    def addTask( self, task:KWCallbackArg ) -> None:
        raise NotImplementedError
        self._tasks.append( KWCallback.make( task ) )

    @reloadingMethod
    def runDeferredTasks(self, context:EvaluationContext) -> None: ...

    @reloadingMethod
    def dumpLoopTimings( self, count:int, minE:Optional[float]=None, minF:Optional[float]=None, **kwds:StrAnyDict ) -> list[Any]: ...

    @reloadingMethod
    def getNextFrame(self) ->ProfileFrameBase: ...

    @reloadingMethod
    def nliGetContainers(self) -> Iterable[NliContainerMixin[NamedLocalIdentifiable]]|None: ...

    @reloadingMethod
    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]|None: ...

    @reloadingMethod
    def launchProject(self, globals:Optional[StrAnyDict]=None, verbose:bool = False ) -> Any: ...

    @reloadingMethod
    def renameIdentifiables(self, items:Optional[dict[str,NamedLocalIdentifiable]]=None, verbose:bool = False ): ...
    
    @reloadingMethod
    def _finishInit(self) -> None: ...

    _rCollect:RefreshablePrdInvAct
    
    
    def run( self ):
        self.asyncManager.asyncMainLoop()
        self.__runExitTasks()


    _renameIdentifiablesItems :dict[str,NamedLocalIdentifiable]

addReloadableClass(MainManager)
#addReloadableClass( MainManager )

_sayMainImport.complete(globals())
