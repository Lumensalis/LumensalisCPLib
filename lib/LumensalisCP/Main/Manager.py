import LumensalisCP.Debug

from LumensalisCP.Identity.Local import NamedLocalIdentifiableList
import time, math, asyncio, traceback, os, gc, wifi, displayio
import busio, board
import collections

from LumensalisCP.CPTyping import *
from LumensalisCP.common import *

from LumensalisCP.util.kwCallback import KWCallback
from LumensalisCP.util.bags import Bag

from LumensalisCP.Controllers.ConfigurableBase import ConfigurableBase
from LumensalisCP.Controllers.Identity import ControllerIdentity, ControllerNVM
from .ControlVariables import ControlVariable, IntermediateVariable

from ..Scenes.Manager import SceneManager, Scene
from ..Triggers.Timer import PeriodicTimerManager

from .Expressions import EvaluationContext, UpdateContext
from .Shutdown import ExitTask
from LumensalisCP.Debug import Debuggable 
from .I2CProvider import I2CProvider

import LumensalisCP.Main.Dependents
import LumensalisCP.Main.Updates

from LumensalisCP.Main.Profiler import Profiler, ProfileFrameBase, ProfileSnapEntry

from . import _preMainConfig

import LumensalisCP.Main.ProfilerRL
LumensalisCP.Main.ProfilerRL._rl_setFixedOverheads()
from LumensalisCP.Shields.Base import ShieldBase

import adafruit_connection_manager

def _early_collect(tag:str):
    _preMainConfig.gcm.runCollection(force=True)
        
class MainManager(ConfigurableBase, I2CProvider, Debuggable):
    
    theManager : "MainManager"|None = None
    ENABLE_EEPROM_IDENTITY = False
    profiler: Profiler
    shields:NamedLocalIdentifiableList[ShieldBase]
    
    @staticmethod
    def initOrGetManager():
        rv = MainManager.theManager
        if rv is None:
            rv = MainManager()
            assert MainManager.theManager is rv
        return rv
    
    def __init__(self, config = None, **kwds ):
        assert MainManager.theManager is None
        MainManager.theManager = self
        _preMainConfig.gcm.main = self
        self.__cycle = 0
        

        #self.__startNs = time.monotonic_ns()
        self.__startNow = time.monotonic()
        self._when:TimeInSeconds = self.getNewNow()

        from LumensalisCP.Main.Dependents import MainRef
        MainRef._theManager = self
        
        self._privateCurrentContext = EvaluationContext(self)
        #def fetchCurrentContext( context:UpdateContext|None ) -> UpdateContext:
        #   return context or self._privateCurrentContext
        #LumensalisCP.Main.Updates.UpdateContext.fetchCurrentContext = fetchCurrentContext
        UpdateContext._patch_fetchCurrentContext(self)

        self.profiler = Profiler(self._privateCurrentContext )
        
        self.__asyncTaskCreators = []
        self.__preFirstRunCallbacks:List[Callable] = []
        self.__socketPool = None
        
        Debuggable._getNewNow = self.getNewNow
        mainConfigDefaults = dict(
            TTCP_HOSTNAME = os.getenv("TTCP_HOSTNAME")
        )
        displayio.release_displays()
        super().__init__(config, defaults=mainConfigDefaults, **kwds )
        Debuggable.__init__(self)
        self.name = "MainManager"
        
        _early_collect("mid manager init")

        I2CProvider.__init__( self, config=self.config, main=self )
  
        self.__identity = ControllerIdentity(self)
        self._when = self.newNow
        
        self._printStatCycles = 5000

        self.cyclesPerSecond = 100
        self.cycleDuration = 0.01

        self._webServer = None
        self.__deferredTasks = collections.deque( [], 99, True )
        self.__audio = None
        self.__dmx : "LumensalisCP.Lights.DMXManager.DMXManager"|None = None

        self._tasks:List[Callable] = []
        self.__shutdownTasks:List[ExitTask] = []
        self.shields = NamedLocalIdentifiableList(parent=self)
        

        self._controlVariables:Mapping[str,ControlVariable] = {}
        self._controlVariables:Mapping[str,ControlVariable] = {}
        self._monitorTargets = {}

        self._timers = PeriodicTimerManager(main=self)

        self._scenes = SceneManager(main=self)
        self.__TerrainTronics = None

        print( f"MainManager options = {self.config.options}" )
        _early_collect("end manager init")
    
    def makeRef(self):
        return LumensalisCP.Main.Dependents.MainRef(self)

    @property
    def identity(self) -> ControllerIdentity: return self.__identity
    
    @property
    def TerrainTronics(self):
        if self.__TerrainTronics is None:
            from TerrainTronics.Factory import TerrainTronicsFactory
            self.__TerrainTronics = TerrainTronicsFactory( main = self )
        return self.__TerrainTronics
    
    @property
    def when(self) -> TimeInSeconds:
        return self._when 
    
    cycle = property( lambda self: self.__cycle )
    millis = property( lambda self: int( self._when * 1000) )
    seconds:float = property( lambda self: self._when )
    
    def getNewNow( self ) -> TimeInSeconds:
        #ns = time.monotonic_ns()
        #return (ns - self.__startNs) * 0.000000001
        now = time.monotonic()
        return now - self.__startNow


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
    def dmx(self):
        if self.__dmx is None:
            import LumensalisCP.Lights.DMXManager
            self.__dmx = LumensalisCP.Lights.DMXManager.DMXManager( self )
            
            self.__asyncTaskCreators.append( self.__dmx.createAsyncTasks )

        return self.__dmx
    
    @property
    def socketPool(self):
        if self.__socketPool is None:
            
            import adafruit_connection_manager
            if not wifi.radio.connected:
                ssid = os.getenv("CIRCUITPY_WIFI_SSID")
                self.sayAtStartup("Connecting to %r", ssid)
                wifi.radio.connect(ssid, os.getenv("CIRCUITPY_WIFI_PASSWORD"))
            #import socketpool
            #self.__socketPool = socketpool.SocketPool(wifi.radio)
            #self.sayAtStartup( "wifi.radio.start_dhcp()" )
            #wifi.radio.start_dhcp()
            pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
            self.__socketPool = pool
        return self.__socketPool
        
    def callLater( self, task ):
        self.__deferredTasks.append( KWCallback.make( task ) )

    def __runExitTasks(self):
        print( "running Main exit tasks" )
        for task in self.__shutdownTasks:
            task.shutdown()
            
    def addExitTask(self,task:ExitTask|Callable):
        if not isinstance( task, ExitTask ):
            task = ExitTask( main=self,task=task)
            
        self.__shutdownTasks.append(task)

    def addControlVariable( self, name, *args, **kwds ) -> ControlVariable:
        variable = ControlVariable( name, *args,**kwds )
        self._controlVariables[name] = variable
        self.infoOut( f"added ControlVariable {name}")
        return variable

    def addIntermediateVariable( self, name, *args, **kwds ) -> IntermediateVariable:
        variable = IntermediateVariable( name, *args,**kwds )
        self._controlVariables[name] = variable
        self.infoOut( f"added Variable {name}")
        variable.updateValue( self._privateCurrentContext )
        return variable

    def addScene( self, name:str, *args, **kwds ) -> Scene:
        scene = self._scenes.addScene( name, *args, **kwds )
        return scene
    
    def addScenes( self, *names:str ) -> List[Scene]:
        return [self.addScene(name) for name in names]
    
    def sayAtStartup( self, fmt, *args ):
        print( "-----" )
        print( f"STARTUP {self.getNewNow():0.3f}: {safeFmt(fmt,*args)}" )
        
    def addBasicWebServer( self, *args, **kwds ):
        from LumensalisCP.HTTP.BasicServer import BasicServer
        self.sayAtStartup( "addBasicWebServer %r, %r ", args, kwds )
        server = BasicServer( *args, main=self, **kwds )
        self._webServer = server
        for v in self._controlVariables.values():
            server.monitorControlVariable( v )
            
        self.__asyncTaskCreators.append( server.createAsyncTasks )
        
        def startWebServer():
            #pool = self.socketPool
            #wifi.radio.start_dhcp()
            if wifi.radio.ipv4_address is not None:
                address = str(wifi.radio.ipv4_address)
                self.sayAtStartup( "startWebServer on %r ", address )
                self._webServer.start(address)
            else:
                self.sayAtStartup( "no address for startWebServer" )

        self.__preFirstRunCallbacks.append( startWebServer )
        return server

    def handleWsChanges( self, changes:dict ):
        
        # print( f"handleWsChanges {changes}")
        key = changes['name']
        val = changes['value']
        v = self._controlVariables.get(key,None)
        if v is not None:
            v.setFromWs( val )
        else:
            self.warnOut( f"missing cv {key} in {self._controlVariables.keys()} for wsChanges {changes}")
    
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
        self.__audio = Audio( *args, main=self,**kwds )
        return self.__audio

    
    def movingValue( self, min=0, max=100, duration:float =1.0 ):
        base = math.floor( self._when / duration ) * duration
        subSpan = self._when - base
        spanRatio = subSpan / duration
        value = ((max - min)*spanRatio) + min
        return value

        
    def addTask( self, task ):
        
        self._tasks.append( KWCallback.make( task ) )
        
    def __runDeferredTasks(self):
        while len( self.__deferredTasks ):
            task = self.__deferredTasks.popleft()
            print( f"running deferred {task}")
            try:
                task()
            except Exception as inst:
                SHOW_EXCEPTION( inst, "exception on deferred task %r", task )

    def dumpLoopTimings( self, count, minE=None, minF=None, **kwds ):
        rv = []
        i = self._privateCurrentContext.updateIndex
        #count = min(count, len(self.__taskLoopTimings))
        # count = min(count,self.profiler.timingsLength)

        
        while count and i >= 0:
            count -= 1
            frame = self.profiler.timingForUpdate( i )
            
            if frame is not None:
                frameData =  frame.jsonData(minE = minE, minF = minF, **kwds )
                if frameData is not None:
                    rv.append( frameData )
            i -= 1
        return rv

    async def taskLoop( self ):
        self.__priorSleepWhen = self.getNewNow()
        self.infoOut( "starting manager main run" )
        _early_collect("end manager init")
        self.__priorSleepWhen = self.getNewNow()
        
        mlc = _preMainConfig._mlc
        nextWait = self.getNewNow()
        
        try:
            for cb in self.__preFirstRunCallbacks:
                cb()
            context = self._privateCurrentContext

            self._when = self.getNewNow()
            
            activeFrame = None
            def getNextFrame( ) -> ProfileFrameBase:
                now = self.getNewNow()
                self._when = now
                #priorWhen = self._when
                self._privateCurrentContext.reset(now)
                context = self._privateCurrentContext
                
                if mlc.ENABLE_PROFILE:
                    newFrame = self.profiler.nextNewFrame(context, eSleep = now  - self.__priorSleepWhen)
                    
                    
                    #memBefore = gc.mem_alloc()
                    #snap = newFrame.snap( 'start' )
                    #snap.augment( 'updateIndex', context.updateIndex )
                    #snap.augment( 'when', now )
                    #snap.augment( 'cycle', self.__cycle )
                else:
                    newFrame = self.profiler.timings[0]
                assert isinstance( newFrame, ProfileFrameBase )
                context.baseFrame  = context.activeFrame = newFrame
                return newFrame
                
            while True:
                with getNextFrame() as activeFrame:
                    context = self._privateCurrentContext
                    #if mlc.ENABLE_PROFILE: 
                    #    snap = activeFrame.currentSnap
                        #snap.augment( 'when', self._when )
                        #snap.augment( 'cycle', self.__cycle )
                    
                    activeFrame.snap( 'preTimers' )
                    #a = gc.mem_alloc()
                    entry = ProfileSnapEntry.makeEntry( "foo", self.when, "bar" )
                    entry.release()
                    
                    #snapNowTest = ( time.monotonic_ns() - activeFrame.loopStartNS )# * 0.000000001
                    #snapNowTest = ( 99 - activeFrame.loopStartNS )# * 0.000000001
        
                    #snapNowTest = time.monotonic_ns()
                    #snapNowTest2 = snapNowTest # time.monotonic_ns()
                    #snapNowTest3 = snapNowTest2 # time.monotonic_ns()
                    
                    activeFrame.snap( 'timers' )
                    self._timers.update( context )
                    if not mlc.MINIMUM_LOOP:

                        activeFrame.snap( 'deferred' )
                        if len( self.__deferredTasks ):
                            self.__runDeferredTasks()
                    
                        activeFrame.snap( 'scenes' )
                        self._scenes.run(context)
                        
                        activeFrame.snap( 'i2c' )
                        for target in self.__i2cDevices:
                            target.updateTarget(context)
                            
                        activeFrame.snap( 'tasks' )
                        for task in self._tasks:
                            task()
                            
                        activeFrame.snap( 'shields' )
                        for shield in self.shields:
                            shield.refresh(context)
                            
                        if self._printStatCycles and self.__cycle % self._printStatCycles == 0:
                            self.infoOut( f"cycle {self.__cycle} at {self._when} with {len(self._tasks)} tasks, gmf={gc.mem_free()} cd={self.cycleDuration}" )
                        #self._scenes.run( context )
                        self.cycleDuration = 1.0 / (self.cyclesPerSecond *1.0)
                        
                    #if mlc.ENABLE_PROFILE:
                    #    activeFrame.finish() 

                    self.__priorSleepWhen = self.getNewNow()
                    nextWait += mlc.nextWaitPeriod
    
                await asyncio.sleep( max(0.001,nextWait-self.__priorSleepWhen) ) # self.cycleDuration )
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
