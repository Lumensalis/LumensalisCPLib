
import time, math, asyncio, wifi
import TerrainTronics.I2C.I2CFactory

class ControlVariable(object):
    def __init__(self, name:str, description:str="", kind:str=None, startingValue=None,
                 min = None, max = None ):
        self.name = name
        self.description = description or name
        self.kind = kind
        
        self._min = min
        self._max = max
        
        self._value = startingValue or min or max

    value = property( lambda self: self._value )
    
    def set( self, value ):
        if value != self._value:
            if self._min is not None and value < self._min:
                value = self._min
            elif self._max is not None and value > self._max:
                value = self._max
            
            if value != self._value:
                self._value = value
    
    def move( self, delta ):
        self.set( self._value + delta )

class MainManager(object):
    
    def __init__(self):
        self.__cycle = 0
        self.cyclesPerSecond = 40
        self.tasks = []
        self.when = time.monotonic()
        self.boards = []
        self.webServer = None
        self.controlVariables = {}
        
        self.adafruitFactory =  TerrainTronics.I2C.I2CFactory.AdafruitFactory(main=self)
        
    cycle = property( lambda self: self.__cycle )

    def addControlVariable( self, name, *args, **kwds ):
        variable = ControlVariable( name, *args,**kwds )
        self.controlVariables[name] = variable
        return variable

    def addBasicWebServer( self, *args, **kwds ):
        from TerrainTronics.HTTP.BasicServer import BasicServer
        server = BasicServer( *args, main=self, **kwds )
        self.webServer = server
        for v in self.controlVariables.values():
            server.monitorControlVariable( v )
        return server
    
    async def msDelay( self, milliseconds ):
        await asyncio.sleep( milliseconds * 0.001 )
        
    
    def addCaernarfon( self, *args, **kwds ):
        from TerrainTronics.Caernarfon import CaernarfonCastle
        castle = CaernarfonCastle( *args, main=self, **kwds )
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
            print( "EXCEPTION : {}".format(inst) )
    
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