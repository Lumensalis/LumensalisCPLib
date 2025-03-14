
import time, math, asyncio, wifi, traceback
import TerrainTronics.I2C.I2CFactory
from TerrainTronics.Controllers.ConfigurableBase import ConfigurableBase
from .ControlVariables import ControlVariable

import rainbowio

class MainManager(ConfigurableBase):
    
    def __init__(self, config = None, **kwds ):
        super().__init__(config, **kwds )
        #if config is None:
        #    config = os.getenv("TTCP_CONTROLLER")
        
        self.__cycle = 0
        self.cyclesPerSecond = 40
        self.tasks = []
        self.when = time.monotonic()
        self.boards = []
        self.webServer = None
        self.controlVariables = {}
        
        self.adafruitFactory =  TerrainTronics.I2C.I2CFactory.AdafruitFactory(main=self)
        self.i2cFactory =  TerrainTronics.I2C.I2CFactory.I2CFactory(main=self)
        
    cycle = property( lambda self: self.__cycle )


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
                    print( "cycle {} at {} with {} tasks".format(   
                        self.__cycle, self.when, len(self.tasks)))
                for task in self.tasks:
                    task()
                await asyncio.sleep( 1.0 / (self.cyclesPerSecond *1.0) )
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