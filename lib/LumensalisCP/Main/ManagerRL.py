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
    if self.__i2cProvider is not None:#  and self.__i2cProvider.i2cDevicesContainer is not None:
        yield self.__i2cProvider.i2cDevicesContainer

    #if self._scenes is not None:
    #    yield self._scenes._scenes
    yield self.controlPanels

@_mmMeta.reloadableMethod()
def MainManager_nliGetChildren(self:MainManager) -> Iterable[NamedLocalIdentifiable]:
    if self._scenes is not None:
        yield self._scenes
    #yield self.defaultController
    if self.__dmx is not None:
        yield self.__dmx
    yield self.__tunables
    
@_mmMeta.reloadableMethod()
def launchProject( self:MainManager, globals:Optional[StrAnyDict]=None, verbose:bool = False ) -> None: 
    if globals is not None:
        self.renameIdentifiables( globals, verbose=verbose )
    useWifi = getattr(self, 'useWifi', False)        
    if useWifi:
        self.sayAtStartup( "adding web server" )
        self.addBasicWebServer()
        self.sayAtStartup( "web server added" )
    self.sayAtStartup( "MainManager.launchProject: starting main loop" )
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
                if not val.nliIsInContainer():
                    val.nliSetContainer(self.__anonInputs)
            elif isinstance(val,NamedOutputTarget):
                if not val.nliIsInContainer():
                    val.nliSetContainer(self.__anonOutputs)

@_mmMeta.reloadableMethod()
def MainManager_monitor( self:MainManager, *inputs:InputSource, enableDbgOut:Optional[bool]=None ) ->None :
    for i in inputs:
        if enableDbgOut is not None:
            i.enableDbgOut = enableDbgOut
        self._monitored.append(i) 

@_mmMeta.reloadableMethod()
def handleWsChanges( self:MainManager, changes:StrAnyDict ):
        
        # print( f"handleWsChanges {changes}")

        defaultPanel = self.controlPanels[0]
        key = changes.get( 'name', None )
        if key is not None:
            val = changes['value']
            v = defaultPanel.controls.get(key,None)
            if v is not None:
                v.setFromWs( val )
            else:
                self.warnOut( f"missing cv {key} in {defaultPanel.controls.keys()} for wsChanges {changes}")
        else:
            triggerName = changes.get( 'trigger', None )
            if triggerName is not None:
                trigger = defaultPanel._triggers.get(triggerName,None)
                self.infoOut( f"wsChanges trigger {triggerName}" )
                assert trigger is not None, f"trigger {triggerName} not found in {defaultPanel._triggers.keys()}"
                
                trigger.fireTrigger( self.getContext() )

@_mmMeta.reloadableMethod()
def dumpLoopTimings( self:MainManager, count:int, minE:Optional[float]=None, minF:Optional[float]=None, **kwds:StrAnyDict ) -> list[Any]:
        rv: list[Any] = []
        i = self._privateCurrentContext.updateIndex

        while count and i >= 0:
            count -= 1
            frame = self.profiler.timingForUpdate( i )
            if frame is not None:
                pass
            i -= 1
        return rv
 
@_mmMeta.reloadableMethod()
def getNextFrame(self:MainManager,now:TimeInSeconds) ->ProfileFrameBase:
    self._when = now
    if self.profiler.disabled:
        newFrame = self.profiler.stubFrame
        self._privateCurrentContext.reset(now,newFrame)
        return newFrame

    context = self._privateCurrentContext
    self._privateCurrentContext.reset(now,None)
    eSleep = TimeInSeconds( now - self.asyncLoop.priorSleepWhen )
    newFrame = self.profiler.nextNewFrame(context, eSleep = eSleep ) 
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
