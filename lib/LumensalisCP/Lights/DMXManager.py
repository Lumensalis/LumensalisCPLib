from __future__ import annotations

# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

from LumensalisCP.IOContext import *
from LumensalisCP.Lights.Light import *
from LumensalisCP.Main.Dependents import *
#############################################################################

if TYPE_CHECKING:
    from LumensalisCP.Main.Panel import ControlPanel
    _DMXChannelArgType:TypeAlias = int
    _DMXUniverseArgType:TypeAlias = Any
    _DMXDataList:TypeAlias = list[Any]
#import stupidArtnet
from LumensalisCP.Lights.LCP_StupidArtnetServer import StupidArtnetASIOServer

# pyright: reportPrivateUsage=false

from LumensalisCP.Main.Async import MainAsyncChild, ManagerAsync

T = TypeVar('T')
class DMXWatcher(SimpleInputSource,Generic[T]):
    DMX_CHANNELS:ClassVar[int] = 1

    def __init__(self,  manager:"DMXManager", initialValue:T, 
                 channel:_DMXChannelArgType,
                   #cN:Optional[_DMXChannelArgType]=None,
                     **kwds:Unpack[InputSource.KWDS]
        ) -> None:
        SimpleInputSource.__init__(self,initialValue,**kwds)
        self.__manager = manager
        self.dmxDataOffset = channel-1
        #self.cN = (cN or c1)-1
        manager._nextAvailableChannel = max( manager._nextAvailableChannel, self.dmxDataOffset + self.DMX_CHANNELS)
        self.dmxData = [0] * self.DMX_CHANNELS
        self.newDmxData = [0] * self.DMX_CHANNELS
        self.__localSetting = initialValue
        self.__isLocal = True



    def set( self, value:T, context:EvaluationContext ) -> None:
        """ update _local_ value"""
        value = context.valueOf(value)
        if self.__isLocal:
            if value == self.__localSetting:
                return 
        self.__localSetting = value
        self.__isLocal = True
        SimpleInputSource.set(self,value, context)


    def updateDMX(self, context:EvaluationContext) -> None:
        #self.__manager._settings[self.c1:self.cN]
        changes = 0
        for cIndex in range(self.DMX_CHANNELS):
            v = self.__manager._settings[self.dmxDataOffset + cIndex]
            if self.dmxData[cIndex] != v:
                changes += 1
                self.newDmxData[cIndex] = v
        if changes == 0:
            return
        self.__isLocal = False
        dmxValue =   self.getDmxValue(context)
        if self.enableDbgOut: self.dbgOut( "updateDMX  =  %r", dmxValue)
        SimpleInputSource.set(self,dmxValue, context)

    def getDmxValue(self, context:EvaluationContext) -> T:
        raise NotImplementedError

DMXWatcherT = GenericT(DMXWatcher)

class DMXDimmerWatcher(DMXWatcherT[ZeroToOne]):
    #    def __init__(self,  manager:"DMXManager", c1:_DMXChannelArgType,**kwds:Unpack[DMXWatcher.KWDS]):
    #    super().__init__(manager, 0.0,c1, c1+1, **kwds)
    #    self.__dimmerValue = 0

    def getDmxValue(self, context:EvaluationContext) -> ZeroToOne:
        assert len(self.dmxData) == 1
        return self.dmxData[0]/255.0


class DMX_RGBWatcher(DMXWatcherT[RGB]):
    DMX_CHANNELS = 3

    def __init__(self,  manager:"DMXManager",  initialValue:RGB, channel:_DMXChannelArgType,**kwds:Unpack[DMXWatcher.KWDS]):
        super().__init__(manager, initialValue, channel, **kwds)
        self.__dmxRgbValue = RGB(0,0,0)


    def getDmxValue(self, context:EvaluationContext) -> RGB:
        self.__dmxRgbValue.r =  self.dmxData[0]/255.0
        self.__dmxRgbValue.g = self.dmxData[1]/255.0
        self.__dmxRgbValue.b = self.dmxData[2]/255.0
        return self.__dmxRgbValue

class DMXManager(MainAsyncChild):
    pass

    def __init__(self, **kwds:Unpack[MainAsyncChild.KWDS]):
        super().__init__(**kwds)
        #self.__client = ArtNetClient()
        self._sasServer = StupidArtnetASIOServer(self.main.socketPool) #Create a server with the default port 6454
        self._universe:_DMXUniverseArgType = 0
        self._settings:_DMXDataList = []
        self._watchers:List[DMXWatcher[Any]] = []
        self._nextAvailableChannel = 1
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
    
    @staticmethod
    def _watcherNames(channel:_DMXChannelArgType,**kwds:Unpack[DMXDimmerWatcher.KWDS]):
        name = kwds.get('name', None) 
        displayName = kwds.get('displayName', None)
        if name is None:
            if displayName is not None:
                name = displayName.replace(' ','_').lower()
            else:
                name = f"dmx_dimmer_{channel}"
                displayName = f"DMX Dimmer {channel}"
        if displayName is None:
            displayName = name
        kwds['name'] = name
        kwds['displayName'] = displayName
        return {'name': name, 'displayName': displayName}

    def addDimmerInputs( self, 
                *names:str,
                firstChannel:Optional[_DMXChannelArgType]=None,
                lights:Optional[LightGroup]=None,
                firstLight:int = 0,
                panel:Optional[ControlPanel]=None,
                    # **kwds:Unpack[DMXDimmerWatcher.KWDS]
                ) -> list[DMXDimmerWatcher]:
        """Add multiple dimmer inputs.

        :param firstChannel: The first DMX channel to use. Each subsequent channel will be assigned to the lights in the order they are provided.
        :param lights: lights to automatically connect to dimmer channels
        :type lights: Optional[LightGroup], optional
        :param firstLight: index of the first light to connect, defaults to 0
        :type firstLight: int, optional
        :param panel: Control Panel to add sliders, defaults to None
        :type panel: Optional[ControlPanel], optional
        :rtype: list[DMXDimmerWatcher]
        """

        if firstChannel is None:
            firstChannel = self._nextAvailableChannel
        rv:list[DMXDimmerWatcher] = []
        for i, name in enumerate(names):
            channel = firstChannel + i
            rv.append(self.addDimmerInput(channel, light=lights[i] if lights else None, panel=panel, displayName=name))
        return rv
    
    def __addLightAndSlider( self, watcher:DMXWatcher[T], slider:InputSource|None, light:Light|None, panel:ControlPanel|None ) -> None:
        if light is not None:
            def updateLight(source:InputSource, context:EvaluationContext) -> None:
                val = source.getValue(context)
                source.infoOut( "DIMMER CHANGE %s = %s", watcher.name, val)
                light.setValue(val,context)

            watcher.onChange(updateLight)
            if slider is not None:
                slider.onChange(updateLight)
    
    def addDimmerInput( self, channel:_DMXChannelArgType,
                       initialValue:ZeroToOne=0.0,
                        light:Optional[Light]=None,
                          panel:Optional[ControlPanel]=None,
                           **kwds:Unpack[DMXDimmerWatcher.KWDS]
                ) -> DMXDimmerWatcher:
        piKwds = self._watcherNames(channel, **kwds)
        rv = DMXDimmerWatcher( self, initialValue, channel=channel, **kwds )
        self._watchers.append(rv)

        panelInput = panel.addZeroToOne(0.0,**piKwds) if panel is not None else None
        self.__addLightAndSlider(rv, panelInput, light, panel)

        return rv


    def addRGBInput( self,initialValue:RGB,channel:_DMXChannelArgType ,
                                light:Optional[Light]=None,
                          panel:Optional[ControlPanel]=None,
                           **kwds:Unpack[DMXDimmerWatcher.KWDS]
            ) -> DMX_RGBWatcher:
        piKwds = self._watcherNames(channel, **kwds)
        rv = DMX_RGBWatcher( self,initialValue, channel, **kwds )
        self._watchers.append(rv)

        panelInput = panel.addZeroToOne(0.0,**piKwds) if panel is not None else None
        self.__addLightAndSlider(rv, panelInput, light, panel)

        return rv
    
    async def handle_dmx(self, universe:_DMXUniverseArgType, data:_DMXDataList ):
        print(f"Universe {universe}: {data}")
        self._settings = data

    
    def test_callback(self, data:_DMXDataList, addr:Any=None):
        """Test function to receive callback data."""
        # the received data is an array
        # of the channels value (no headers)
        self.dbgOut( f'Received from {addr} new data [{len(data)}] {data}' )
        context = UpdateContext.fetchCurrentContext(None)
        self._settings = data
        for watcher in self._watchers:
            watcher.updateDMX( context )

        
    async def runAsyncSingleLoop(self, when:TimeInSeconds) -> None:
        await self._sasServer._listenSingleLoop()
