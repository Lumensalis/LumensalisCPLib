import asyncio
from LumensalisCP.IOContext import NamedOutputTarget
from LumensalisCP.Inputs import NamedLocalIdentifiable, InputSource
from LumensalisCP.Main.Profiler import ProfileFrameBase, ProfileSnapEntry
from LumensalisCP.Outputs import OutputTarget
from . import Manager

from LumensalisCP.Identity.Local import NamedLocalIdentifiableContainerMixin, NamedLocalIdentifiableList,NamedLocalIdentifiable

import gc
from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from ._preMainConfig import _mlc, gcm

mlc = _mlc
    
def MainManager_nliContainers(self:Manager.MainManager) -> Iterable[NamedLocalIdentifiableContainerMixin]|None:
    return [self.shields, self._i2cDevicesContainer, self._controlVariables]

def MainManager_nliGetChildren(self:Manager.MainManager) -> Iterable[NamedLocalIdentifiable]|None:
    
    yield self._scenes
    if self.__dmx is not None:
        yield self.__dmx


def MainManager_renameIdentifiables( self:Manager.MainManager, items:dict|None ):
    if items is None:
        items = self._renameIdentifiablesItems
    else:
        self._renameIdentifiablesItems = items
        
    for tag,val in items.items():
        if isinstance(val,NamedLocalIdentifiable):
            if not val.nliIsNamed:
                print( f"renaming {type(val)}:{val.name} to {tag}" )
                val.name = tag

            if isinstance(val,InputSource):
                if val.nliGetContaining() is None:
                    val.nliSetContainer(self.__anonInputs)
            elif isinstance(val,NamedOutputTarget):
                if val.nliGetContaining() is None:
                    val.nliSetContainer(self.__anonOutputs)
                    

def MainManager_handleWsChanges( self:Manager.MainManager, changes:dict ):
        
        # print( f"handleWsChanges {changes}")
        key = changes['name']
        val = changes['value']
        v = self._controlVariables.get(key,None)
        if v is not None:
            v.setFromWs( val )
        else:
            self.warnOut( f"missing cv {key} in {self._controlVariables.keys()} for wsChanges {changes}")

def MainManager_singleLoop( self:Manager.MainManager ): #, activeFrame:ProfileFrameBase):
    with self.getNextFrame() as activeFrame:
        context = self._privateCurrentContext
        #if mlc.ENABLE_PROFILE: 
        #    snap = activeFrame.currentSnap
            #snap.augment( 'when', self._when )
            #snap.augment( 'cycle', self.__cycle )
        
        activeFrame.snap( 'preTimers' )
        #a = gc.mem_alloc()
        entry = ProfileSnapEntry.makeEntry( "foo", self.when, "bar" )
        entry.release()
        
        #snapNowTest = ( time.monotonic_ns() - activeFrame.loopStartNS )# * 0.000000001
        #snapNowTest = ( 99 - activeFrame.loopStartNS )# * 0.000000001

        #snapNowTest = time.monotonic_ns()
        #snapNowTest2 = snapNowTest # time.monotonic_ns()
        #snapNowTest3 = snapNowTest2 # time.monotonic_ns()
        
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
                
            if self._printStatCycles and self.__cycle % self._printStatCycles == 0:
                self.infoOut( f"cycle {self.__cycle} at {self._when} with {len(self._tasks)} tasks, gmf={gc.mem_free()} cd={self.cycleDuration}" )
            #self._scenes.run( context )
            self.cycleDuration = 1.0 / (self.cyclesPerSecond *1.0)
            
        #if mlc.ENABLE_PROFILE:
        #    activeFrame.finish() 

        self.__priorSleepWhen = self.getNewNow()
        self._nextWait += mlc.nextWaitPeriod
        
    #await asyncio.sleep( max(0.001,self._nextWait-self.__priorSleepWhen) ) # self.cycleDuration )
    #self.__cycle += 1        

def MainManager_dumpLoopTimings( self:Manager.MainManager, count, minE=None, minF=None, **kwds ):
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
    
def MainManager_getNextFrame(self) ->ProfileFrameBase:
        now = self.getNewNow()
        self._when = now
        #priorWhen = self._when
        self._privateCurrentContext.reset(now)
        context = self._privateCurrentContext
        
        if _mlc.ENABLE_PROFILE:
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
        