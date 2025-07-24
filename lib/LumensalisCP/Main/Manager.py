from __future__ import annotations
from asyncio import Task

import wifi, displayio

import LumensalisCP.Audio
import LumensalisCP.Main.Dependents
from LumensalisCP.commonPreManager import *
from LumensalisCP.Main import PreMainConfig

from TerrainTronics.Factory import TerrainTronicsFactory

from LumensalisCP.Shields.Base import ShieldBase
from LumensalisCP.Main.I2CProvider import I2CProvider

from LumensalisCP.Main.ControlVariables import ControlPanel

from LumensalisCP.Main import ManagerRL

if TYPE_CHECKING:
    from LumensalisCP.Lights.DMXManager import DMXManager
    import LumensalisCP.Main.Manager
    # from LumensalisCP.Controllers.Config import ControllerConfigArg

import LumensalisCP.Main.ProfilerRL
LumensalisCP.Main.ProfilerRL._rl_setFixedOverheads() # type: ignore

def _early_collect(tag:str):
    PreMainConfig.pmc_gcManager.runCollection(force=True)

class MainManager(NamedLocalIdentifiable, ConfigurableBase, I2CProvider):
    
    class KWDS(ConfigurableBase.KWDS): # type: ignore
        pass
    
    theManager : "MainManager|None" = None
    ENABLE_EEPROM_IDENTITY = False
    profiler: Profiler
    shields:NliList[ShieldBase]
    controlPanels:NliList[ControlPanel]
    _privateCurrentContext:EvaluationContext
    
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
        self.__startNow = time.monotonic()
        self._when:TimeInSeconds = self.getNewNow()
        getMainManager.set(self.__getMMSelf())

        from LumensalisCP.Main.Dependents import MainRef  # pylint: disable=
        MainRef._theManager = self  # type: ignore
        
        self._privateCurrentContext = EvaluationContext(self.__getMMSelf())
        UpdateContext._patch_fetchCurrentContext(self) # type: ignore

        self.profiler = Profiler(self._privateCurrentContext )

        self.__asyncTaskCreators: list[Callable[[], list[Task[None]]]] = []
        self.__preFirstRunCallbacks: list[Callable[[], None]] = []
        self.__socketPool:Any = None
        
        Debuggable._getNewNow = self.getNewNow
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

        self._webServer = None
        self.__deferredTasks: collections.deque[Callable[[], None]] = collections.deque( [], 99, True ) # type: ignore # pylint: disable=all
        self.__audio = None
        self.__dmx :DMXManager|None = None

        self._tasks:List[KWCallback] = []
        self.__shutdownTasks:List[ExitTask] = []
        self.shields = NliList(name='shields',parent=self)


        self.__anonInputs:NliList[InputSource] = NliList(name='inputs',parent=self)
        self.__anonOutputs:NliList[NamedOutputTarget] = NliList(name='outputs',parent=self)
        self.controlPanels = NliList(name='controllers',parent=self)
        self.defaultController = ControlPanel(self)
        self.defaultController.nliSetContainer(self.controlPanels)

        self._monitored:list[InputSource] = []

        self._timers = PeriodicTimerManager(main=self.__getMMSelf())

        self._scenes: SceneManager = SceneManager(main=self.__getMMSelf())
        self.__TerrainTronics = None

        if pmc_mainLoopControl.preMainVerbose: print( f"MainManager options = {self.config.options}" )
        _early_collect("end manager init")
    
    def makeRef(self):
        return LumensalisCP.Main.Dependents.MainRef(self)

    @property
    def identity(self) -> ControllerIdentity: return self.__identity

    @property
    def TerrainTronics(self:'MainManager') -> TerrainTronicsFactory:
        if self.__TerrainTronics is None:
            from TerrainTronics.Factory import TerrainTronicsFactory
            #self.__TerrainTronics = TerrainTronicsFactory( self.__getMMSelf() )
            self.__TerrainTronics = TerrainTronicsFactory( self )
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

    def __getMMSelf(self) -> LumensalisCP.Main.Manager.MainManager:
        """ hack to get around pyright getting confused by self ... ???
        :rtype: LumensalisCP.Main.Manager.MainManager
        """
        # TODO : why is pylance flagging this as wrong?
        return self # type: ignore
    
    @property
    def panel(self) -> ControlPanel:
        """ the default control panel """
        return self.defaultController
    
    @property
    def dmx(self):
        if self.__dmx is None:
            import LumensalisCP.Lights.DMXManager
            self.__dmx = LumensalisCP.Lights.DMXManager.DMXManager( self.__getMMSelf() )
            
            self.__asyncTaskCreators.append( self.__dmx.createAsyncTasks )

        return self.__dmx
    
    @property
    def socketPool(self) -> Any:
        if self.__socketPool is None:
            
            import adafruit_connection_manager # type: ignore
            if not wifi.radio.connected:
                ssid = os.getenv("CIRCUITPY_WIFI_SSID")
                self.sayAtStartup("Connecting to %r", ssid)
                wifi.radio.connect(ssid, os.getenv("CIRCUITPY_WIFI_PASSWORD")) # type: ignore
            #import socketpool
            #self.__socketPool = socketpool.SocketPool(wifi.radio)
            #self.sayAtStartup( "wifi.radio.start_dhcp()" )
            #wifi.radio.start_dhcp()
            pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio) # type: ignore
            self.__socketPool = pool
            
        return self.__socketPool # type: ignore
        
    def callLater( self, task:KWCallbackArg ):
        self.__deferredTasks.append( KWCallback.make( task ) )

    def __runExitTasks(self):
        print( "running Main exit tasks" )
        for task in self.__shutdownTasks:
            task.shutdown()
            
    def addExitTask(self,task:ExitTask|Callable[[], None]|KWCallbackArg):
        if not isinstance( task, ExitTask ):
            task = ExitTask( main=self.__getMMSelf(),task=task)
            
        self.__shutdownTasks.append(task)

    #def addControlVariable( self, *args, **kwds ) -> ControlVariable:
    #    return self.defaultController.addControlVariable( *args, **kwds )

    #def addIntermediateVariable( self,  *args, **kwds ) -> IntermediateVariable:
    #    return self.defaultController.addIntermediateVariable( *args, **kwds )

    def addScene( self, **kwds:Unpack[Scene.KWDS] ) -> Scene:
        scene = self._scenes.addScene( **kwds )
        return scene
    
    def addScenes( self, n:int ):
        #->  Unpack[Tuple[Scene, ...]]:
        return [self.addScene() for _ in range(n)]
        return [self.addScene(name) for name in names]
    
    def sayAtStartup( self, fmt:str, *args:Any ):
        if pmc_mainLoopControl.startupVerbose:
            print( "-----" )
            print( f"{self.getNewNow():0.3f} STARTUP : {safeFmt(fmt,*args)}" )
            
    def addBasicWebServer( self, *args:Any, **kwds:StrAnyDict ):
        from LumensalisCP.HTTP.BasicServer import BasicServer
        self.sayAtStartup( "addBasicWebServer %r, %r ", args, kwds )
        server = BasicServer( *args, main=self.__getMMSelf(), **kwds )
        self._webServer = server

        self.__asyncTaskCreators.append( server.createAsyncTasks )
        
        def startWebServer():
            if wifi.radio.ipv4_address is not None:
                address = str(wifi.radio.ipv4_address)
                self.sayAtStartup( "startWebServer on %r ", address )
                self._webServer.start(address) # type: ignore
            else:
                self.sayAtStartup( "no address for startWebServer" )

        self.__preFirstRunCallbacks.append( startWebServer )
        return server

    def monitor( self, *inputs:InputSource, **kwds:StrAnyDict ) -> None:
        return ManagerRL.MainManager_monitor(self.__getMMSelf(), *inputs, **kwds )


    def handleWsChanges( self, changes:dict ):
        return ManagerRL.MainManager_handleWsChanges(self.__getMMSelf(), changes)

    async def msDelay( self, milliseconds ):
        await asyncio.sleep( milliseconds * 0.001 )
    
    @property
    def audio(self) -> "LumensalisCP.Audio.Audio":
        if self.__audio is None:
            self.addI2SAudio()
            assert self.__audio is not None
        return self.__audio

    def addI2SAudio(self, *args, **kwds ) -> "LumensalisCP.Audio.Audio":
        from LumensalisCP.Audio import Audio
        assert self.__audio is None
        self.__audio = Audio( main=self.__getMMSelf(), *args,**kwds )
        return self.__audio

    def movingValue( self, min=0, max=100, duration:float =1.0 ):
        base = math.floor( self._when / duration ) * duration
        subSpan = self._when - base
        spanRatio = subSpan / duration
        value = ((max - min)*spanRatio) + min
        return value

    def addTask( self, task:KWCallbackArg ):
        self._tasks.append( KWCallback.make( task ) )
        
    def __runDeferredTasks(self):
        while len( self.__deferredTasks ):
            task = self.__deferredTasks.popleft()
            self.infoOut( f"running deferred {task}")
            try:
                task()
            except Exception as inst:
                SHOW_EXCEPTION( inst, "exception on deferred task %r", task )

    def dumpLoopTimings( self, count, minE=None, minF=None, **kwds ):
        return ManagerRL.MainManager_dumpLoopTimings(self.__getMMSelf(), count, minE=minE, minF=minF, **kwds )

    def getNextFrame(self) ->ProfileFrameBase:
        return ManagerRL.MainManager_getNextFrame(self ) # type: ignore
    
    def nliGetContainers(self) -> Iterable[NliContainerMixin]|None:
        return ManagerRL.MainManager_nliContainers(self ) # type: ignore
   
    def nliGetChildren(self) -> Iterable[NamedLocalIdentifiable]|None:
        return ManagerRL.MainManager_nliGetChildren(self ) # type: ignore

    def launchProject(self, globals:Optional[dict[str,Any]]=None, verbose:bool = False ):
        return ManagerRL.MainManager_launchProject(self.__getMMSelf(), globals, verbose=verbose )

    def renameIdentifiables(self, items:Optional[dict[str,NamedLocalIdentifiable]]=None, verbose:bool = False ):
        return ManagerRL.MainManager_renameIdentifiables(self.__getMMSelf(), items, verbose )
    
    async def taskLoop( self ):
        self.__priorSleepWhen = self.getNewNow()
        self.infoOut( "starting manager main run" )
        _early_collect("end manager init")
        self.__priorSleepWhen = self.getNewNow()
        
        mlc = PreMainConfig.pmc_mainLoopControl
        self._nextWait = self.getNewNow()
        
        try:
            for cb in self.__preFirstRunCallbacks:
                cb()
            context = self._privateCurrentContext

            self._when = self.getNewNow()
            while True:
                ManagerRL.MainManager_singleLoop(self) # type: ignore
                self.__latestSleepDuration = max(0.001, self._nextWait-self.__priorSleepWhen )
                
                await asyncio.sleep( self.__latestSleepDuration ) 
                self.__cycle += 1    

        except Exception as inst:
            self.errOut( "EXCEPTION in task loop : {}".format(inst) )
            print(''.join(traceback.format_exception(inst)))
            
        except KeyboardInterrupt:
            self.errOut( "KeyboardInterrupt!" )
            self.__runExitTasks()
            raise

        self.__runExitTasks()
    
    def run( self ):
        
        async def main():      
            asyncTasks = [
                asyncio.create_task( self.taskLoop() )
            ]
            for atc in self.__asyncTaskCreators:
                asyncTasks.extend(atc())
            await asyncio.gather( *asyncTasks )
            
        asyncio.run( main() )
        self.__runExitTasks()


    _renameIdentifiablesItems :dict[str,NamedLocalIdentifiable]