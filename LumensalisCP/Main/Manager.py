
import time, math, asyncio, traceback, os, gc, rainbowio, wifi, displayio

import LumensalisCP.I2C.I2CFactory
from LumensalisCP.Controllers.ConfigurableBase import ConfigurableBase
from .ControlVariables import ControlVariable

class MainManager(ConfigurableBase):
    
    def __init__(self, config = None, **kwds ):
        mainConfigDefaults = dict(
            TTCP_HOSTNAME = os.getenv("TTCP_HOSTNAME")
        )
        displayio.release_displays()
        super().__init__(config, defaults=mainConfigDefaults, **kwds )

        self.__cycle = 0
        self.cyclesPerSecond = 100
        self.cycleDuration = 0.01
        self.tasks = []
        self.when = time.monotonic()
        self.boards = []
        self.webServer = None
        self.controlVariables = {}
        
        self.adafruitFactory =  LumensalisCP.I2C.I2CFactory.AdafruitFactory(main=self)
        self.i2cFactory =  LumensalisCP.I2C.I2CFactory.I2CFactory(main=self)
        
        print( f"MainManager options = {self.config.options}" )
        
    cycle = property( lambda self: self.__cycle )
    millis = property( lambda self: int( self.when * 1000) )

    def wheel( self, val:float ): return rainbowio.colorwheel(val)
    
    def addControlVariable( self, name, *args, **kwds ):
        variable = ControlVariable( name, *args,**kwds )
        self.controlVariables[name] = variable
        print( f"added ControlVariable {name}")
        return variable

    def addBasicWebServer( self, *args, **kwds ):
        from TerrainTronics.HTTP.BasicServer import BasicServer
        server = BasicServer( *args, main=self, **kwds )
        self.webServer = server
        for v in self.controlVariables.values():
            server.monitorControlVariable( v )
        return server
    
    def handleWsChanges( self, changes:dict ):
        
        # print( f"handleWsChanges {changes}")
        key = changes['name']
        val = changes['value']
        v = self.controlVariables.get(key,None)
        if v is not None:
            v.setFromWs( val )
        else:
            print( f"missing cv {key} in {self.controlVariables.keys()} for wsChanges {changes}")
    
    async def msDelay( self, milliseconds ):
        await asyncio.sleep( milliseconds * 0.001 )
        
    
    def addCaernarfon( self, config=None, **kwds ):
        from TerrainTronics.Caernarfon import CaernarfonCastle
        castle = CaernarfonCastle( config=config, main=self, **kwds )
        self.boards.append(castle)
        return castle
    
    def movingValue( self, min=0, max=100, duration:float =1.0 ):
        base = math.floor( self.when / duration ) * duration
        subSpan = self.when - base
        spanRatio = subSpan / duration
        value = ((max - min)*spanRatio) + min
        return value

    def addTask( self, task ):
        
        self.tasks.append( task )
        
    
    async def taskLoop( self ):

        print( "starting manager main run" )
        try:
            while True:
                self.when = time.monotonic()
                
                if self.__cycle % 100 == 0:
                    print( f"cycle {self.__cycle} at {self.when} with {len(self.tasks)} tasks, gmf={gc.mem_free()} cd={self.cycleDuration}" )
                for task in self.tasks:
                    task()
                self.cycleDuration = 1.0 / (self.cyclesPerSecond *1.0)
                await asyncio.sleep( 0 ) # self.cycleDuration )
                self.__cycle += 1

        except Exception as inst:
            print( "EXCEPTION in tsak loop : {}".format(inst) )
            print(traceback.format_exception(inst))

    
    def run( self ):
        if self.webServer is not None:
            self.webServer.start(str(wifi.radio.ipv4_address))
        async def main():      
            asyncTasks = [
                asyncio.create_task( self.taskLoop() )
            ]
            if self.webServer is not None:
                asyncTasks.extend(self.webServer.createAsyncTasks())
            await asyncio.gather( *asyncTasks )
            
        asyncio.run( main() )