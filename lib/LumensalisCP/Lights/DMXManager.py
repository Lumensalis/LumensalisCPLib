from __future__ import annotations

# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

from LumensalisCP.IOContext import *
from LumensalisCP.Lights.Light import *
from LumensalisCP.Main.Dependents import *

#############################################################################

#import stupidArtnet
from LumensalisCP.Lights.LCP_StupidArtnetServer import StupidArtnetASIOServer

# pyright: reportPrivateUsage=false

from LumensalisCP.Main.Async import MainAsyncChild, ManagerAsync

_DMXChannelArgType:TypeAlias = int
_DMXUniverseArgType:TypeAlias = Any
_DMXDataList:TypeAlias = list[Any]

class DMXWatcher(InputSource):
    def __init__(self, name:str, manager:"DMXManager", c1:_DMXChannelArgType, cN:Optional[_DMXChannelArgType]=None):
        super().__init__(name=name)
        self.__manager = manager
        self.c1 = c1-1
        self.cN = (cN or c1)-1
        self.data = []
        
    def update(self):
        newData = self.__manager._settings[self.c1:self.cN]
        if self.data != newData:
            self.data = newData
            #self.dbgOut( "data changed to %r", self.data )
            print( f" {self.name} data changed to {self.data}" )
            self.derivedUpdate()
            
    def derivedUpdate(self) -> None: raise NotImplementedError

class DMXDimmerWatcher(DMXWatcher):
    def __init__(self, name:str, manager:"DMXManager", c1:_DMXChannelArgType):
        super().__init__(name, manager, c1, c1+1 )
        self.__dimmerValue = 0
        
    def derivedUpdate(self):
        assert len(self.data) == 1
        self.__dimmerValue = self.data[0]/255.0
        self.dbgOut( "derivedUpdate  =  %r", self.__dimmerValue)

    def getDerivedValue(self, context:EvaluationContext) -> Any:
        #self.dbgOut( "getDerivedValue returning %r", self.__dimmerValue)
        return self.__dimmerValue


class DMX_RGBWatcher(DMXWatcher):
    def __init__(self, name:str, manager:"DMXManager", c1:_DMXChannelArgType):
        super().__init__(name, manager, c1, c1+3 )
        self.__rgbValue = RGB(0,0,0)
        
    def derivedUpdate(self):
        ensure( len(self.data) == 3, "expected 3, not %r in %r", len(self.data), self.data )
        self.__rgbValue =  RGB( self.data[0]/255.0, self.data[1]/255.0, self.data[2]/255.0 )

    def getDerivedValue(self, context:EvaluationContext) -> Any:
        return self.__rgbValue



class DMXManager(MainAsyncChild):
    pass

    def __init__(self, **kwds:Unpack[MainAsyncChild.KWDS]):
        super().__init__(**kwds)
        #self.__client = ArtNetClient()
        self._sasServer = StupidArtnetASIOServer(self.main.socketPool) #Create a server with the default port 6454
        self._universe:_DMXUniverseArgType = 0
        self._settings:_DMXDataList = []
        self._watchers:List[DMXWatcher] = []
        # For every universe we would like to receive,
        # add a new listener with a optional callback
        # the return is an id for the listener
        self.u1_listener = self._sasServer.register_listener( # type: ignore
            self._universe, callback_function=self.test_callback)


        # or disable simplified mode to use nets and subnets as per spec
        # subnet = 1 (would have been universe 17 in simplified mode)
        # net = 0
        # a.register_listener(universe, sub=subnet, net=net,
        #                    setSimplified=False, callback_function=test_callback)

    def asyncTaskStats(self, out:Optional[dict[str,Any]]=None) -> dict[str,Any]:
        rv = super().asyncTaskStats(out)
        rv['settings'] = len(self._settings)
        rv['inverse'] = self._universe
        rv['watchers'] = self._watchers
        return rv
    
    def addDimmerInput( self, name:str, channel:_DMXChannelArgType ):
        rv = DMXDimmerWatcher( name, self, channel )
        self._watchers.append(rv)
        return rv


    def addRGBInput( self, name:str, channel:_DMXChannelArgType ):
        rv = DMX_RGBWatcher( name, self, channel )
        self._watchers.append(rv)
        return rv
    
    async def handle_dmx(self, universe:_DMXUniverseArgType, data:_DMXDataList ):
        print(f"Universe {universe}: {data}")
        self._settings = data

    
    def test_callback(self, data:_DMXDataList, addr:Any=None):
        """Test function to receive callback data."""
        # the received data is an array
        # of the channels value (no headers)
        self.dbgOut( f'Received from {addr} new data [{len(data)}] {data}' )
        self._settings = data
        for watcher in self._watchers:
            watcher.update( )

        
    async def runAsyncSingleLoop(self, when:TimeInSeconds) -> None:
        await self._sasServer._listenSingleLoop()
