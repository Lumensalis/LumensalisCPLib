
import LumensalisCP.Main.Manager
from LumensalisCP.commonPreManager import *

from LumensalisCP.Main import Manager

from .PreMainConfig import pmc_mainLoopControl, pmc_gcManager

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager


mlc = pmc_mainLoopControl
    
def MainManager_nliContainers(self:MainManager) -> Iterable[NamedLocalIdentifiableContainerMixin]|None:
    yield self.shields
    yield self._i2cDevicesContainer
    yield self.controllers

def MainManager_nliGetChildren(self:MainManager) -> Iterable[NamedLocalIdentifiable]|None:
    yield self._scenes
    #yield self.defaultController
    if self.__dmx is not None:
        yield self.__dmx


def MainManager_launchProject( self:MainManager, globals:Optional[dict]=None, verbose:bool = False ): 
    if globals is not None:
        self.renameIdentifiables( globals, verbose=verbose )
    self.addBasicWebServer()
    self.run()



def MainManager_renameIdentifiables( self:MainManager, items:Optional[dict]=None, verbose:bool = False ):
    if items is None:
        items = self._renameIdentifiablesItems
    else:
        self._renameIdentifiablesItems = items
        
    for tag,val in items.items():
        if isinstance(val,NamedLocalIdentifiable):
            if not val.nliIsNamed:
                if verbose: print( f"renaming {type(val)}:{val.name} to {tag}" )
                val.name = tag

            if isinstance(val,InputSource):
                if val.nliGetContaining() is None:
                    val.nliSetContainer(self.__anonInputs)
            elif isinstance(val,NamedOutputTarget):
                if val.nliGetContaining() is None:
                    val.nliSetContainer(self.__anonOutputs)
                    

def MainManager_handleWsChanges( self:MainManager, changes:dict ):
        
        # print( f"handleWsChanges {changes}")
        key = changes['name']
        val = changes['value']
        v = self._controlVariables.get(key,None)
        if v is not None:
            v.setFromWs( val )
        else:
            self.warnOut( f"missing cv {key} in {self._controlVariables.keys()} for wsChanges {changes}")

def MainManager_singleLoop( self:MainManager ): #, activeFrame:ProfileFrameBase):
    with self.getNextFrame() as activeFrame:
        context = self._privateCurrentContext
        
        activeFrame.snap( 'preTimers' )
        entry = ProfileSnapEntry.makeEntry( "foo", self.when, "bar" )
        entry.release()

        activeFrame.snap( 'timers' )
        self._timers.update( context )
        if not mlc.MINIMUM_LOOP:

            activeFrame.snap( 'deferred' )
            if len( self.__deferredTasks ):
                self.__runDeferredTasks()
        
            activeFrame.snap( 'scenes' )
            self._scenes.run(context)
            
            activeFrame.snap( 'i2c' )
            for target in self.__i2cDevices:
                target.updateTarget(context)
                
            activeFrame.snap( 'tasks' )
            for task in self._tasks:
                task()
                
            activeFrame.snap( 'shields' )
            for shield in self.shields:
                shield.refresh(context)
                
            if pmc_mainLoopControl.printStatCycles and self.__cycle % pmc_mainLoopControl.printStatCycles == 0:
                #self.infoOut( f"cycle {self.__cycle} at {self._when} with {len(self._tasks)} tasks, gmf={gc.mem_free()} cd={self.cycleDuration}" )
                self.infoOut( "cycle %d at %.3f : scene %s ip=%s with %d tasks, gmf=%d cd=%r",
                             self.__cycle, self._when, 
                             self.scenes.currentScene, self._webServer,
                             len(self._tasks), gc.mem_free(), self.cycleDuration
                        )
            #self._scenes.run( context )
            self.cycleDuration = 1.0 / (self.cyclesPerSecond *1.0)
            
        #if mlc.ENABLE_PROFILE:
        #    activeFrame.finish() 

        self.__priorSleepWhen = self.getNewNow()
        self._nextWait += mlc.nextWaitPeriod
        
    #await asyncio.sleep( max(0.001,self._nextWait-self.__priorSleepWhen) ) # self.cycleDuration )
    #self.__cycle += 1        

def MainManager_dumpLoopTimings( self:MainManager, count, minE=None, minF=None, **kwds ):
        rv = []
        i = self._privateCurrentContext.updateIndex
        #count = min(count, len(self.__taskLoopTimings))
        # count = min(count,self.profiler.timingsLength)

        
        while count and i >= 0:
            count -= 1
            frame = self.profiler.timingForUpdate( i )
            
            if frame is not None:
                frameData =  frame.jsonData(minE = minE, minF = minF, **kwds )
                if frameData is not None:
                    rv.append( frameData )
            i -= 1
        return rv
    
def MainManager_getNextFrame(self:MainManager) ->ProfileFrameBase:
        now = self.getNewNow()
        self._when = now
        #priorWhen = self._when
        self._privateCurrentContext.reset(now)
        context = self._privateCurrentContext
        
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
        