from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler
__sayMainManagerRLImport = getImportProfiler( globals(), reloadable=True )

from LumensalisCP.commonPreManager import *
from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl #, pmc_gcManager
from LumensalisCP.util.Reloadable import ReloadableModule

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager

# pylint: disable=protected-access, bad-indentation, missing-function-docstring
# pylint: disable=no-member, redefined-builtin, unused-argument
# pyright: reportPrivateUsage=none

#############################################################################

mlc = pmc_mainLoopControl

_module = ReloadableModule( 'LumensalisCP.Main.Manager' )
_mmMeta = _module.reloadableClassMeta('MainManager', stripPrefix='MainManager_')

@_mmMeta.reloadableMethod()
def MainManager_nliGetContainers(self:MainManager) -> Iterable[NliContainerMixin[Any]]|None:
    yield self.shields
    yield self.i2cDevicesContainer
    yield self.controlPanels

@_mmMeta.reloadableMethod()
def MainManager_nliGetChildren(self:MainManager) -> Iterable[NamedLocalIdentifiable]|None:
    yield self._scenes
    #yield self.defaultController
    if self.__dmx is not None:
        yield self.__dmx

@_mmMeta.reloadableMethod()
def MainManager_launchProject( self:MainManager, globals:Optional[StrAnyDict]=None, verbose:bool = False ) -> None: 
    if globals is not None:
        self.renameIdentifiables( globals, verbose=verbose )
    useWifi = getattr(self, 'useWifi', False)        
    if useWifi:
        self.addBasicWebServer()
    self.run()

@_mmMeta.reloadableMethod()
def MainManager_renameIdentifiables( self:MainManager, items:Optional[dict[str,NamedLocalIdentifiable]]=None, verbose:bool = False ):
    if items is None:
        items = self._renameIdentifiablesItems
        assert items is not None, "No items to rename, and no _renameIdentifiablesItems set."
    else:
        self._renameIdentifiablesItems = items

    for tag,val in items.items():
        if isinstance(val,NamedLocalIdentifiable): # type: ignore
            if not val.nliIsNamed:
                if verbose: print( f"renaming {type(val)}:{val.name} to {tag}" )
                val.name = tag

            if isinstance(val,InputSource):
                if val.nliGetContaining() is None:
                    val.nliSetContainer(self.__anonInputs)
            elif isinstance(val,NamedOutputTarget):
                if val.nliGetContaining() is None:
                    val.nliSetContainer(self.__anonOutputs)

@_mmMeta.reloadableMethod()
def MainManager_monitor( self:MainManager, *inputs:InputSource, enableDbgOut:Optional[bool]=None ) ->None :
    for i in inputs:
        if enableDbgOut is not None:
            i.enableDbgOut = enableDbgOut
        self._monitored.append(i) 

@_mmMeta.reloadableMethod()
def MainManager_handleWsChanges( self:MainManager, changes:StrAnyDict ):
        
        # print( f"handleWsChanges {changes}")
        key = changes['name']
        val = changes['value']
        defaultPanel = self.controlPanels[0]
        v = defaultPanel.controls.get(key,None)
        if v is not None:
            v.setFromWs( val )
        else:
            self.warnOut( f"missing cv {key} in {defaultPanel.controls.keys()} for wsChanges {changes}")

@_mmMeta.reloadableMethod()
def singleLoop( self:MainManager ): #, activeFrame:ProfileFrameBase):
    with self.getNextFrame(): #  as activeFrame:
        context = self._privateCurrentContext

        self._refreshables.process(context, context.when)
        self._timers.update( context )
        if not mlc.MINIMUM_LOOP:


            if len( self.__deferredTasks ):
                self.runDeferredTasks(context)
        
            #activeFrame.snap( 'scenes' )
            self._scenes.run(context)
            
            #with context.subFrame('i2c'):
            #    for target in self.__i2cDevices:
            #        target.updateDevice(context)

            #with context.subFrame('tasks'):
            #    for task in self._tasks:
            #        task()

            #with context.subFrame( 'shields' ):
            #    for shield in self.shields:
            #        shield.refresh(context)
                    
 
            #self._scenes.run( context )
            self.cycleDuration = 1.0 / (self.cyclesPerSecond *1.0)
            
        #if mlc.ENABLE_PROFILE:
        #    activeFrame.finish() 

        self.__priorSleepWhen = self.getNewNow()
        self._nextWait += mlc.nextWaitPeriod # type: ignore

    #await asyncio.sleep( max(0.001,self._nextWait-self.__priorSleepWhen) ) # self.cycleDuration )
    #self.__cycle += 1        

@_mmMeta.reloadableMethod()
def dumpLoopTimings( self:MainManager, count:int, minE:Optional[float]=None, minF:Optional[float]=None, **kwds:StrAnyDict ) -> list[Any]:
        rv: list[Any] = []
        i = self._privateCurrentContext.updateIndex
        #count = min(count, len(self.__taskLoopTimings))
        # count = min(count,self.profiler.timingsLength)

        
        while count and i >= 0:
            count -= 1
            frame = self.profiler.timingForUpdate( i )
            
            if frame is not None:

                pass
            i -= 1
        return rv
 
@_mmMeta.reloadableMethod()
def MainManager_getNextFrame(self:MainManager) ->ProfileFrameBase:
        now = self.getNewNow()
        self._when = now
        #priorWhen = self._when
        self._privateCurrentContext.reset(now)
        context = self._privateCurrentContext

        if True:
            eSleep = TimeInSeconds( now - self.__priorSleepWhen )
            newFrame = self.profiler.nextNewFrame(context, eSleep = eSleep ) 
        else:
            if pmc_mainLoopControl.ENABLE_PROFILE:
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

@_mmMeta.reloadableMethod()
def runDeferredTasks(self:MainManager, context:EvaluationContext) -> None: # type: ignore
    with context.subFrame('deferredTasks'):

        while len( self.__deferredTasks ):
            task = self.__deferredTasks.popleft()
            self.infoOut( f"running deferred {task}")
            try:
                task()
            except Exception as inst:
                SHOW_EXCEPTION( inst, "exception on deferred task %r", task )

__sayMainManagerRLImport.complete(globals())
