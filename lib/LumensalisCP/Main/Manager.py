import LumensalisCP.Debug

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

from .Expressions import EvaluationContext
from .Shutdown import ExitTask
from LumensalisCP.Debug import Debuggable 
from .I2CProvider import I2CProvider

import LumensalisCP.Main.Dependents
import LumensalisCP.Main.Updates

from LumensalisCP.Main.Profiler import Profiler

from . import _mconfig


def _early_collect(tag:str):
    _mconfig.gcm.runCollection(force=True)
        
class MainManager(ConfigurableBase, I2CProvider, Debuggable):
    
    theManager : "MainManager"|None = None
    ENABLE_EEPROM_IDENTITY = False
    profiler: Profiler
    
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
        _mconfig.gcm.main = self
        self.__cycle = 0
        
        LumensalisCP.Main.Updates._getCurrentUpdateContext = self.getContext
        
        self.__startNs = time.monotonic_ns()
        self._when:TimeInSeconds = self.newNow
        self.profiler = Profiler()
        
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
        from LumensalisCP.Main.Dependents import MainRef
        MainRef._theManager = self
        
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
        self._boards = []
        

        self._controlVariables:Mapping[str,ControlVariable] = {}
        self._monitorTargets = {}

        self.__evContext = EvaluationContext(self)
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
        ns = time.monotonic_ns()
        return (ns - self.__startNs) * 0.000000001


    @property
    def newNow( self ) -> TimeInSeconds: return self.getNewNow()

    @property
    def scenes(self) -> SceneManager: return self._scenes
    
    @property
    def timers(self) -> PeriodicTimerManager: return self._timers
    
    @property
    def latestContext(self)->EvaluationContext: return  self.__evContext

    def getContext(self)->EvaluationContext: 
        return  self.__evContext

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
            import socketpool
            self.__socketPool = socketpool.SocketPool(wifi.radio)
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
        # self._controlVariables[name] = variable
        self.infoOut( f"added Variable {name}")
        variable.updateValue( self.__evContext )
        return variable

    def addScene( self, name:str, *args, **kwds ) -> Scene:
        scene = self._scenes.addScene( name, *args, **kwds )
        return scene
    
    def addBasicWebServer( self, *args, **kwds ):
        from LumensalisCP.HTTP.BasicServer import BasicServer
        server = BasicServer( *args, main=self, **kwds )
        self._webServer = server
        for v in self._controlVariables.values():
            server.monitorControlVariable( v )
            
        self.__asyncTaskCreators.append( server.createAsyncTasks )
        
        def startWebServer():
            self._webServer.start(str(wifi.radio.ipv4_address))

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
        i = self.__evContext.updateIndex
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
        
        mlc = _mconfig._mlc
        activeFrame = None
        if mlc.ENABLE_PROFILE:
            def snapTime(m,**kwds):
                return activeFrame.snap(m,**kwds)
        else:
            def snapTime(*args,**kwds): return None

        nextWait = self.getNewNow()
        
        try:
            context = self.__evContext

            self._when = self.getNewNow()
            
            while True:
                self._when = now = self.getNewNow()
                #priorWhen = self._when
                self.__evContext.reset(now)
                context = self.__evContext
                
                if mlc.ENABLE_PROFILE:
                    activeFrame = self.profiler.nextNewFrame(context.updateIndex, eSleep = now  - self.__priorSleepWhen)
                    context.baseFrame  = context.activeFrame = activeFrame
                    
                    #memBefore = gc.mem_alloc()
                    snap = snapTime( 'start' )
                    snap.augment( updateIndex = context.updateIndex, when=now, cycle=self.__cycle
                             #, memBefore=memBefore
                            )
                else:
                    activeFrame = self.profiler.timings[0]
                    context.baseFrame  = context.activeFrame = activeFrame
                    
                
                
                
                self._timers.update( context )
                if not mlc.MINIMUM_LOOP:

                    snapTime( 'deferred' )
                    if len( self.__deferredTasks ):
                        self.__runDeferredTasks()
                
                    snapTime( 'scenes' )
                    self._scenes.run(context)
                    
                    snapTime( 'i2c' )
                    for target in self.__i2cDevices:
                        target.updateTarget(context)
                        
                    snapTime( 'tasks' )
                    for task in self._tasks:
                        task()
                        
                    snapTime( 'boards' )
                    for board in self._boards:
                        board.refresh(context)
                        
                    if self._printStatCycles and self.__cycle % self._printStatCycles == 0:
                        self.infoOut( f"cycle {self.__cycle} at {now} with {len(self._tasks)} tasks, gmf={gc.mem_free()} cd={self.cycleDuration}" )
                    #self._scenes.run( context )
                    self.cycleDuration = 1.0 / (self.cyclesPerSecond *1.0)
                    
                if mlc.ENABLE_PROFILE:
                    activeFrame.finish() 

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
