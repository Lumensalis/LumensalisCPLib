
import time, math, asyncio, traceback, os, gc, rainbowio, wifi, displayio

import LumensalisCP.I2C.I2CFactory
from LumensalisCP.Controllers.ConfigurableBase import ConfigurableBase
from .ControlVariables import ControlVariable

from ..Scenes.Manager import SceneManager, Scene
from LumensalisCP.CPTyping import Any, Callable, Mapping, List
from LumensalisCP.CPTyping import override
from .Expressions import EvaluationContext

class MainManager(ConfigurableBase):
    
    theManager : "MainManager"|None = None
    
    def __init__(self, config = None, **kwds ):
        assert MainManager.theManager is None
        MainManager.theManager = self
        mainConfigDefaults = dict(
            TTCP_HOSTNAME = os.getenv("TTCP_HOSTNAME")
        )
        displayio.release_displays()
        super().__init__(config, defaults=mainConfigDefaults, **kwds )

        self.__cycle = 0
        self.cyclesPerSecond = 100
        self.cycleDuration = 0.01
        self._tasks:List[Callable] = []
        self._when = time.monotonic()
        self._boards = []
        self._webServer = None
        self._controlVariables:Mapping[str,ControlVariable] = {}
        self._monitorTargets = {}
        self._scenes = SceneManager(main=self)
        self._printStatCycles = 1000
        self.adafruitFactory =  LumensalisCP.I2C.I2CFactory.AdafruitFactory(main=self)
        self.i2cFactory =  LumensalisCP.I2C.I2CFactory.I2CFactory(main=self)
        self.__evContext = EvaluationContext()
        
        print( f"MainManager options = {self.config.options}" )
    
    when = property( lambda self: self._when )
    cycle = property( lambda self: self.__cycle )
    millis = property( lambda self: int( self._when * 1000) )
    seconds:float = property( lambda self: self._when )

    def wheel255( self, val:float ): return rainbowio.colorwheel(val)
    
    def wheel1( self, val:float ): return rainbowio.colorwheel(val*255.0)
    
    def addControlVariable( self, name, *args, **kwds ) -> ControlVariable:
        variable = ControlVariable( name, *args,**kwds )
        self._controlVariables[name] = variable
        print( f"added ControlVariable {name}")
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
            print( f"missing cv {key} in {self._controlVariables.keys()} for wsChanges {changes}")
    
    async def msDelay( self, milliseconds ):
        await asyncio.sleep( milliseconds * 0.001 )
        
    
    def addCaernarfon( self, config=None, **kwds ):
        from TerrainTronics.Caernarfon import CaernarfonCastle
        castle = CaernarfonCastle( config=config, main=self, **kwds )
        self._boards.append(castle)
        return castle
    
    def movingValue( self, min=0, max=100, duration:float =1.0 ):
        base = math.floor( self._when / duration ) * duration
        subSpan = self._when - base
        spanRatio = subSpan / duration
        value = ((max - min)*spanRatio) + min
        return value

    def addTask( self, task ):
        
        self._tasks.append( task )
        
    
    async def taskLoop( self ):

        print( "starting manager main run" )
        try:
            while True:
                self.__evContext.reset()
                self._when = time.monotonic()
                self._scenes.run(self.__evContext)
                if self._printStatCycles and self.__cycle % self._printStatCycles == 0:
                    print( f"cycle {self.__cycle} at {self._when} with {len(self._tasks)} tasks, gmf={gc.mem_free()} cd={self.cycleDuration}" )
                for task in self._tasks:
                    task()
                self._scenes.run( self.__evContext )
                self.cycleDuration = 1.0 / (self.cyclesPerSecond *1.0)
                await asyncio.sleep( 0 ) # self.cycleDuration )
                self.__cycle += 1

        except Exception as inst:
            print( "EXCEPTION in tsak loop : {}".format(inst) )
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