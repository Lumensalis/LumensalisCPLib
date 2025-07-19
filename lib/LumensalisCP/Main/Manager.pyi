from LumensalisCP.I2C.I2CDevice import I2CDevice
import LumensalisCP.Lights
from LumensalisCP.commonPreManager import *

from LumensalisCP.Main import PreMainConfig

import LumensalisCP.I2C.I2CFactory
import LumensalisCP.I2C.Adafruit.AdafruitI2CFactory
import busio
from LumensalisCP.Lights.DMXManager import DMXManager

from LumensalisCP.Shields.Base import ShieldBase

from LumensalisCP.HTTP.BasicServer import BasicServer
from LumensalisCP.Audio import Audio
from TerrainTronics.Factory import TerrainTronicsFactory

from LumensalisCP.Main.ControlVariables import Controller, ControlVariable 
import LumensalisCP.Lights.DMXManager

class MainManager(NamedLocalIdentifiable, ConfigurableBase, I2CProvider):
    
    theManager : MainManager|None

    socketPool : Any # SocketPool
    profiler: Profiler
    shields:NamedLocalIdentifiableList[ShieldBase]
    defaultController:Controller
    controllers:NamedLocalIdentifiableList[Controller]
    
    
    __anonInputs : NamedLocalIdentifiableList[InputSource]
    __anonOutputs : NamedLocalIdentifiableList[NamedOutputTarget]
    __latestSleepDuration:TimeSpanInSeconds
    _monitored:list[InputSource]
    _nextWait:TimeInSeconds
    __priorSleepWhen:TimeInSeconds
    _privateCurrentContext:EvaluationContext
    _renameIdentifiablesItems:dict[str,Any]
    _scenes: SceneManager
    __shutdownTasks:List[ExitTask]
    __startNow: TimeInSeconds
    _tasks:List[Callable]
    _timers: PeriodicTimerManager
    _webServer:BasicServer|None
    _when: TimeInSeconds
    
    @staticmethod
    def initOrGetManager()->MainManager: ...

    def __init__(self, config = None, **kwds ): ...
 
    def makeRef(self)-> LumensalisCP.Main.Dependents.MainRef: pass

    
    @property
    def identity(self) -> ControllerIdentity: pass
    
    @property
    def TerrainTronics(self) ->TerrainTronicsFactory: pass
    
    @property
    def when(self) -> TimeInSeconds: pass


    @property
    def cycle(self) -> int : ...
    @property
    def millis(self) -> TimeInMS : ...
    @property
    def seconds(self) -> TimeInSeconds: ...
    def getNewNow( self ) -> TimeInSeconds: ...

    @property
    def scenes(self) -> SceneManager: pass
    
    @property
    def timers(self) -> PeriodicTimerManager: pass
    
    latestContext:EvaluationContext
     
    def getContext(self)->EvaluationContext: pass

    @property
    def dmx(self) -> LumensalisCP.Lights.DMXManager.DMXManager: ...
    __dmx: LumensalisCP.Lights.DMXManager.DMXManager
    
    def callLater( self, task ): pass

    def launchProject(self, globals:Optional[dict]=None, verbose:bool = False ): ...
            
    def addExitTask(self,task:ExitTask|Callable): pass
        
    def _addI2CDevice(self, target:I2CDevice ): pass
   
   # TODO: mirror ControlVariable.__init__ 
    def addControlVariable( self, *args, **kwds ) -> ControlVariable: pass
    
    # TODO: mirror IntermediateVariable.__init__ 
    def addIntermediateVariable( self, *args, **kwds ) -> IntermediateVariable: pass
        
    def addScene( self, name:Optional[str]=None, *args, **kwds ) -> Scene: pass
    
    def addScenes( self, n:int ) -> list[Scene]: pass
    
    def sayAtStartup( self, fmt:str, *args ): ...
    
    def addBasicWebServer( self, *args, **kwds ) -> BasicServer: pass

    def handleWsChanges( self, changes:dict ): pass
        
    
    async def msDelay( self, milliseconds ): pass
    
    @property
    def audio(self) -> Audio: pass

    def addI2SAudio(self, *args, **kwds ) -> Audio: pass

    
    def movingValue( self, min=0, max=100, duration:float =1.0 ) -> float: pass
        
    def _addBoardI2C( self, board, i2c:busio.I2C ): pass

    def addTask( self, task ): pass

    def dumpLoopTimings( self, count:int, minE:Optional[TimeSpanInSeconds]=None, minF:Optional[TimeSpanInSeconds]=None, **kwds ): pass

    def getNextFrame(self) ->ProfileFrameBase: ...
    
    async def taskLoop( self ): pass

    def run( self ): pass

    def renameIdentifiables(self, d:dict[str,Any], verbose:bool = False ): ...
    
    def monitor( self, *inputs:InputSource, **kwds ) -> None: ...