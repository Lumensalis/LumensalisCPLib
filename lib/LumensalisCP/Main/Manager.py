from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayMainImport = getImportProfiler( "Main.Manager", globals() )

# pyright: reportUnusedImport=false

import wifi, displayio, random, os

import LumensalisCP.Main.Dependents
from LumensalisCP.commonPreManager import *
from LumensalisCP.Main import PreMainConfig
from LumensalisCP.Main.PreMainConfig import sayAtStartup


from LumensalisCP.Temporal.Refreshable import Refreshable
from LumensalisCP.Temporal.RefreshableList import RootRefreshableList
from LumensalisCP.util.Reloadable import addReloadableClass, reloadingMethod
from LumensalisCP.Main import GetManager 
from LumensalisCP.Temporal.Refreshable import *
from LumensalisCP.Main.Raw import RawAccess
from LumensalisCP.Tunable.Group import TunableGroup

#from LumensalisCP.Main import ManagerRL
#from LumensalisCP.Main import Manager2RL
#from LumensalisCP.Main.Async import ManagerAsync

if TYPE_CHECKING:
    from LumensalisCP.Lights.DMXManager import DMXManager
    from LumensalisCP.Main.Manager import MainManager
    from LumensalisCP.Audio import Audio
    from LumensalisCP.Main.Profiler import Profiler, ProfileFrameBase
    from LumensalisCP.Main.MainAsync import MainAsyncLoop, MainGCLoop
    from LumensalisCP.HTTP.BasicServer import BasicServer
    from TerrainTronics.Factory import TerrainTronicsFactory
    from LumensalisCP.Shields.Base import ShieldBase
    from LumensalisCP.Main.I2CProvider import I2CProvider
    from LumensalisCP.Main.Panel import ControlPanel
    from LumensalisCP.I2C.Factory import I2CFactory
    from LumensalisCP.I2C.Adafruit.Factory import AdafruitFactory
    from LumensalisCP.Main.Async import MainAsyncChild, ManagerAsync
    from LumensalisCP.Controllers.ConfigurableBase import ConfigurableBase, ControllerConfig

import LumensalisCP.Main.ProfilerRL

#############################################################################

_sayMainImport.parsing()

LumensalisCP.Main.ProfilerRL._rl_setFixedOverheads() # type: ignore

def _early_collect(tag:str):
    PreMainConfig.pmc_gcManager.checkAndRunCollection(force=True)


#############################################################################

class MainManager( NamedLocalIdentifiable ): #, I2CProvider, ConfigurableBase, ):
    
    #class KWDS(ConfigurableBase.KWDS): # type: ignore
    class KWDS(NamedLocalIdentifiable.KWDS): # type: ignore        
        pass

    theManager : MainManager|None = None
    ENABLE_EEPROM_IDENTITY = False
    profiler: Profiler
    shields:NliList[ShieldBase]
    controlPanels:NliList[ControlPanel]
    _privateCurrentContext:EvaluationContext
    asyncLoop:MainAsyncLoop
    gcLoop:MainGCLoop
    useWifi:bool
    configuration:ConfigurableBase
    config:ControllerConfig 
    sessionUuid:str


    @staticmethod
    def initManager(*args:Any,**kwargs:Any) -> "MainManager":
        assert MainManager.theManager is None
        rv = MainManager()
        assert MainManager.theManager is rv
        return rv
    
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

    def __init__(self, unitTesting:bool=False, **kwds:Unpack[KWDS] ) -> None:
        assert MainManager.theManager is None
        MainManager.theManager = self
        NamedLocalIdentifiable.__init__(self,"main")
        self.unitTesting = unitTesting
        self.__installManager()


        self._when = self.newNow
        self._webServer:BasicServer|None = None
        self._rrDeferred:RefreshablePrdInvAct|None = None
        self._rrCollect:RefreshablePrdInvAct|None = None
        self.__deferredTasks: collections.deque[Callable[[], None]] = collections.deque( [], 99, True ) # type: ignore # pylint: disable=all
        self.__audio = None
        self.__dmx :DMXManager|None = None
        self.__shutdownTasks:List[ExitTask] = []
        self.shields = NliList(name='shields',parent=self)
        
        self.__anonInputs:NliList[InputSource] = NliList(name='inputs',parent=self)
        self.__anonOutputs:NliList[NamedOutputTarget] = NliList(name='outputs',parent=self)
        self.controlPanels = NliList(name='panels',parent=self)
        self.__rootPanel:ControlPanel|None = None

        
        self._monitored:list[InputSource] = []
        self._timers:PeriodicTimerManager|None = None
        self._scenes: SceneManager|None = None
        self.__i2cProvider:I2CProvider|None = None
        
        self.__TerrainTronics = None
        self.__tunables = TunableGroup(name='tunables')
        self.sessionUuid = f"{self.name}_{os.urandom(4).hex()}" 
        self.raw = RawAccess(self)
        
        if not self.unitTesting:
            from LumensalisCP.Main import ManagerRL
            from LumensalisCP.Main import Manager2RL
            self.__liveInit(**kwds)

            self._finishInit()

        _early_collect("end manager init")

    def __installManager(self):
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
        self.__socketPool = None
        
        Debuggable._getNewNow = self.getNewNow # type: ignore

        self.__cycle = 0

    @reloadingMethod
    def __liveInit(self, **kwds:Any): ...

    def makeRef(self):
        return LumensalisCP.Main.Dependents.MainRef(self)

    @property
    def tunables(self) -> TunableGroup:
        return self.__tunables

    @property
    def refreshables(self) -> RootRefreshableList:
        """ The root refreshable list for the main manager. """
        return self._refreshables

    @property
    def identity(self) -> ControllerIdentity: 
        return self.__identity

    @property
    def i2cProvider(self) -> I2CProvider:
        assert self.__i2cProvider is not None
        return self.__i2cProvider

    @property
    def adafruitFactory(self) -> AdafruitFactory:
        return self.i2cProvider.adafruitFactory

    @property
    def i2cFactory(self) -> I2CFactory:
        return self.i2cProvider.i2cFactory

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
    def cycle(self) -> int : 
        try:
            return self.asyncLoop.cycle 
        except AttributeError:
            return self.__cycle
    
    @property
    def millis(self) -> TimeInMS : return int(self._when * 1000)
    @property
    def seconds(self) -> TimeInSeconds: return self._when 
    
    def getNewNow( self ) -> TimeInSeconds:
        #ns = getOffsetNow_ns()
        #return (ns - self.__startNs) * 0.000000001
        return getOffsetNow()
        #now = getOffsetNow()
        #return now - self.__startNow # type: ignore # pylint: disable=all


    @property
    def newNow( self ) -> TimeInSeconds: return self.getNewNow()

    @property
    def scenes(self) -> SceneManager:
        if self._scenes is None:
            from LumensalisCP.Scenes.Manager import SceneManager
            self._scenes = SceneManager(main=self,name="scenes")
        return self._scenes
    
    @property
    def timers(self) -> PeriodicTimerManager: 
        if self._timers is None:
            from LumensalisCP.Triggers.Timer import PeriodicTimerManager
            self._timers = PeriodicTimerManager(main=self)
        return self._timers
    
    @property
    def latestContext(self)->EvaluationContext: return  self._privateCurrentContext

    def getContext(self)->EvaluationContext: 
        return  self._privateCurrentContext

    @property
    def panel(self) -> ControlPanel:
        """ the default control panel """
        if self.__rootPanel is not None:
            return self.__rootPanel
        from LumensalisCP.Main.Panel import ControlPanel

        self.__rootPanel = ControlPanel(main=self)
        self.__rootPanel.nliSetContainer(self.controlPanels)
        
        return self.__rootPanel
    
    def addPanel( self, **kwds:Unpack[ControlPanel.KWDS] ) -> ControlPanel:
        kwds.setdefault('main', self)
        from LumensalisCP.Main.Panel import ControlPanel
        panel = ControlPanel( **kwds)
        self.controlPanels.append(panel)
        return panel

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
        
    def callLater( self, task:Callable[[],None] ) -> None:
        self.__deferredTasks.append( task )
        assert self._rrDeferred is not None
        if not self._rrDeferred.isActiveRefreshable:
            self._rrDeferred.activate(self.getContext())

    def __runExitTasks(self):
        print( "running Main exit tasks" )
        for task in self.__shutdownTasks:
            task.shutdown()
            
    def addExitTask(self,task:ExitTask|Callable[[], None]):
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
        scene = self.scenes.addScene( **kwds )
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
    def getNextFrame(self, now:TimeInSeconds) ->ProfileFrameBase: ...

    @reloadingMethod
    def nliGetContainers(self) -> NliGetContainersRVT: ...

    def nliHasContainers(self) -> bool:
        return True

    @reloadingMethod
    def nliGetChildren(self) -> NliGetChildrenRVT:
        yield from ()

    def nliHasChildren(self) -> bool: return True

    @reloadingMethod
    def launchProject(self, globals:Optional[StrAnyDict]=None, verbose:bool = False ) -> Any: ...

    @reloadingMethod
    def renameIdentifiables(self, items:Optional[dict[str,NamedLocalIdentifiable]]=None, verbose:bool = False ): ...
    
    @reloadingMethod
    def _showLoop(self, context:EvaluationContext) -> None: ...

    @reloadingMethod
    def _finishInit(self) -> None: ...

    _rCollect:RefreshablePrdInvAct
    _showLoopData: dict[str, Any] 
    
    def run( self ):
        self.asyncManager.asyncMainLoop()
        self.__runExitTasks()

    _renameIdentifiablesItems :dict[str,NamedLocalIdentifiable]
    __cycle:int
    #__startNow:TimeInSeconds 
    _when:TimeInSeconds
    _refreshables: RootRefreshableList
    profiler: Profiler
    asyncManager:ManagerAsync
    __socketPool:Any 
    __identity: ControllerIdentity

addReloadableClass(MainManager, checkMethods=False)
#addReloadableClass( MainManager )

_sayMainImport.complete(globals())
