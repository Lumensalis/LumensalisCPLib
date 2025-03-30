

import LumensalisCP.Debug

import time, math, asyncio, traceback, os, gc, rainbowio, wifi, displayio
import  busio, board

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *

import LumensalisCP.I2C.I2CFactory
import LumensalisCP.I2C.I2CTarget
import LumensalisCP.I2C.Adafruit.AdafruitI2CFactory
from LumensalisCP.Controllers.ConfigurableBase import ConfigurableBase
from .ControlVariables import ControlVariable

from ..Scenes.Manager import SceneManager, Scene
from ..Triggers.Timer import PeriodicTimerManager

from .Expressions import EvaluationContext
from LumensalisCP.Debug import Debuggable 
class MainManager(ConfigurableBase, Debuggable):
    
    theManager : "MainManager"|None = None
    
    def __init__(self, config = None, **kwds ):
        assert MainManager.theManager is None
        MainManager.theManager = self
        self.__startNs = time.monotonic_ns()
        self._when:TimeInSeconds = self.newNow
        
        mainConfigDefaults = dict(
            TTCP_HOSTNAME = os.getenv("TTCP_HOSTNAME")
        )
        displayio.release_displays()
        super().__init__(config, defaults=mainConfigDefaults, **kwds )
        Debuggable.__init__(self)
        self.name = "MainManager"
        
        self.__cycle = 0
        self.cyclesPerSecond = 100
        self.cycleDuration = 0.01
        self._tasks:List[Callable] = []

        self._boards = []
        self._webServer = None
        self._controlVariables:Mapping[str,ControlVariable] = {}
        self._monitorTargets = {}
        self._scenes = SceneManager(main=self)
        self._timers = PeriodicTimerManager(main=self)
        self._printStatCycles = 1000
        self.adafruitFactory =  LumensalisCP.I2C.Adafruit.AdafruitI2CFactory.AdafruitFactory(main=self)
        self.i2cFactory =  LumensalisCP.I2C.I2CFactory.I2CFactory(main=self)
        self.__defaultI2C:busio.I2C = None
        self.__evContext = EvaluationContext(self)
        self.__i2cTargets:List["LumensalisCP.I2C.I2CTarget.I2CTarget"] = []
        
        print( f"MainManager options = {self.config.options}" )
    
    @property
    def when(self) -> TimeInSeconds:
        return self._when 
    
    cycle = property( lambda self: self.__cycle )
    millis = property( lambda self: int( self._when * 1000) )
    seconds:float = property( lambda self: self._when )
    
    @property
    def newNow( self ) -> TimeInSeconds:
        ns = time.monotonic_ns()
        return (ns - self.__startNs) * 0.000000001

    @property
    def defaultI2C(self):
        return self.__defaultI2C or board.I2C()
    
    @property
    def scenes(self) -> SceneManager: return self._scenes
    
    @property
    def timers(self) -> PeriodicTimerManager: return self._timers

    def _addI2CTarget(self, target:"LumensalisCP.I2C.I2CTarget.I2CTarget" ):
        self.__i2cTargets.append(target)
        
    def wheel255( self, val:float ): return rainbowio.colorwheel(val)
    
    def wheel1( self, val:float ): return rainbowio.colorwheel(val*255.0)
    
    def addControlVariable( self, name, *args, **kwds ) -> ControlVariable:
        variable = ControlVariable( name, *args,**kwds )
        self._controlVariables[name] = variable
        self.infoOut( f"added ControlVariable {name}")
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
        
    
    def addCaernarfon( self, config=None, **kwds ):
        from TerrainTronics.Caernarfon import CaernarfonCastle
        castle = CaernarfonCastle( config=config, main=self, **kwds )
        self._boards.append(castle)
        return castle
    
    def addHarlech( self, config=None, **kwds ):
        from TerrainTronics.Harlech import HarlechCastle
        castle = HarlechCastle( config=config, main=self, **kwds )
        self._boards.append(castle)
        return castle
    
    def movingValue( self, min=0, max=100, duration:float =1.0 ):
        base = math.floor( self._when / duration ) * duration
        subSpan = self._when - base
        spanRatio = subSpan / duration
        value = ((max - min)*spanRatio) + min
        return value

    def _addBoardI2C( self, board, i2c:busio.I2C ):
        if self.__defaultI2C is None:
            self.__defaultI2C = i2c

    def addTask( self, task ):
        
        self._tasks.append( task )
        
    
    async def taskLoop( self ):

        self.infoOut( "starting manager main run" )
        try:
            while True:
                self.__evContext.reset()
                context = self.__evContext
                self._when = self.newNow
                self._timers.update( context )
                self._scenes.run(context)
                for target in self.__i2cTargets:
                    target.updateTarget(context)
                for task in self._tasks:
                    task()
                if self._printStatCycles and self.__cycle % self._printStatCycles == 0:
                    self.infoOut( f"cycle {self.__cycle} at {self._when} with {len(self._tasks)} tasks, gmf={gc.mem_free()} cd={self.cycleDuration}" )
                #self._scenes.run( context )
                self.cycleDuration = 1.0 / (self.cyclesPerSecond *1.0)
                await asyncio.sleep( 0 ) # self.cycleDuration )
                self.__cycle += 1

        except Exception as inst:
            self.errOut( "EXCEPTION in task loop : {}".format(inst) )
            print(traceback.format_exception(inst))

    
    def run( self ):
        if self._webServer is not None:
            self._webServer.start(str(wifi.radio.ipv4_address))
        async def main():      
            asyncTasks = [
                asyncio.create_task( self.taskLoop() )
            ]
            if self._webServer is not None:
                asyncTasks.extend(self._webServer.createAsyncTasks())
            await asyncio.gather( *asyncTasks )
            
        asyncio.run( main() )