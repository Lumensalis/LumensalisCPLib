
import LumensalisCP.Main.Updates
from LumensalisCP.Main._mconfig import _mlc
import time, math, asyncio, traceback, os, gc, wifi, displayio
import busio, board
import collections

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
from LumensalisCP.util.kwCallback import KWCallback
from LumensalisCP.util.bags import Bag
from . import ProfilerRL

from ._mconfig import gcm, _mlc
import gc
import asyncio.lock

class ProfileWriteConfig(object):
    
    def __init__(self,target,minE=None,minEB=None,minF=None,minSubF=None,minB=None, **kwds):
 
        self.target = target
        self.minB = minB if minB is not None else 1024
        self.minEB = minEB if minEB is not None else self.minB
        self.minE = minE if minE is not None else -1
        self.minF =  minF or self.minE 
        self.minSubF = minSubF or 0
        
    def __repr__(self):
        return f"mE={self.minE} mF={self.minF} mSF={self.minSubF} mB={self.minB} mEB={self.minEB}"
    
    def writeLine( self, fmt:str, *args ):
        self.target.write( safeFmt( fmt, *args ) )
        self.target.write( "\r\n" )
        

class ReleasablePool(object):
    _freeHead:"Releasable"
    
    def __init__(self, cls ):
        self._freeHead = None
        self._allocs = 0
        self._releases = 0
        self._rIndex = 0
        self._cls = cls
        self._lock = asyncio.lock.Lock()
    
class Releasable(object):
    
    @classmethod 
    def getReleasablePool(cls):
        rv = getattr(cls,'__rp',None)
        if rv is None:
            rv = ReleasablePool(cls)
            setattr(cls,'__rp',rv)
        return rv
        
    @classmethod
    def makeEntry(cls,*args, **kwds):
        rp = cls.getReleasablePool()
        #with rp._lock:
        if True:
            if rp._freeHead:
                entry = rp._freeHead
                rp._freeHead = entry._nextFree
                entry._nextFree = None
                entry.reset(*args, **kwds)
            else:
                entry = cls(*args, **kwds)
                rp._allocs += 1
            assert entry._nextFree is None and not entry._inUse
            entry._inUse = True
            entry._rIndex = rp._rIndex
            rp._rIndex += 1
            
        return entry

    _inUse:bool
    _nextFree:"Releasable"|None
    _rIndex:int
    
    def __init__(self):
        self._inUse = False
        self._nextFree = None
        
    def release(self):
        assert self._inUse and self._nextFree is None
        self._inUse = False
        rp = self.getReleasablePool()
        self._nextFree = rp._freeHead
        rp._freeHead = self
        rp._releases += 1
        self.releaseNested()

    def releaseNested(self):
        pass            

class ProfileFrameEntry(Releasable): 
    __slots__ = ["name","name2","lw","e","_nest","_nesting","etc"]
    __defaultEtc = {}
    
    gcFixedOverhead = 112
    
    name:str
    name2:str|None
    lw: TimeSpanInSeconds
    e: TimeSpanInSeconds
    _nest:  "ProfileSubFrame"|None
    _nesting:  bool
    etc: Dict


    def __init__(self,tag:str, when:TimeInSeconds, name2:str|None = None):
        super().__init__()
        self.reset(tag,when, name2)

    def releaseNested(self):
        if self._nesting:
            assert self._nest is not None
            self._nesting = False
            self._nest.release()

    def shouldProfileMemory(self):
        return gcm.PROFILE_MEMORY_ENTRIES
    
    def usedByProfile(self):
        if self.rawUsedGC:
            if self._nesting:
                return self._nest.usedByProfile() + self.gcFixedOverhead
            return  self.gcFixedOverhead
        return self.gcFixedOverhead
    
    @property 
    def usedGC( self ):
        return self.rawUsedGC - self.usedByProfile()
        
    def reset( self, name:str, when:TimeInSeconds, name2:str|None = None ):
        self.name = name
        self.lw = when
        self.e = 0.0
        self.etc = self.__defaultEtc
        self._nesting = False
        self.allocGc = gc.mem_alloc() if self.shouldProfileMemory() else 0
            
        self.rawUsedGC = 0
        self.name2 = name2

        
    def augment( self, **kwds ):
        self.etc = kwds
        
    @property 
    def nest( self ) -> "ProfileSubFrame"|None: return self._nest if self._nesting else None

    def releaseNested(self):
        if self._nesting:
            assert self._nest is not None
            nest = self._nest
            self._nest = None
            self._nesting = False
            nest.release()

    def subFrame(self, context, name:str|None=None, name2:str|None = None) -> 'ProfileSubFrame':
        assert not self._nesting 
        self._nest = ProfileSubFrame.makeEntry(context,name, name2)
        self._nesting = True
        return self._nest

    def writeOn(self,config:ProfileWriteConfig,indent=''):
        return ProfilerRL.ProfileFrameEntry_writeOn(self,config,indent)
    
    def jsonData(self,**kwds):
        rv = collections.OrderedDict(lw=self.lw, e=self.e, id=id(self), **self.etc)
        subFrame = self.nest
        if subFrame is not None:
            assert subFrame is not self
            rv['nest'] = subFrame.jsonData() # **kwds)
        return rv

class ProfileFrameBase(Releasable): 
    __entries:List[ProfileFrameEntry]
    __usedEntries:int
    e:TimeSpanInSeconds
    when : TimeSpanInSeconds
    loopStartNS : int
    priorStartNS: int
    latestStartNS: int
    currentSnap: ProfileFrameEntry
    index: int
    depth: int = 0
    
    nextFrameIndex = 1

    gcFixedOverhead = 112
    
    #_resets = 0
    #_allocs = 0
    
    def __init__(self):
        super().__init__()
        self.__entries = []
        self._name = '--'
        self.__usedEntries = 0
        #ProfileFrameBase._allocs += 1
        #self.reset()
        
                
    def usedByProfile(self):
        rv = self.gcFixedOverhead
        for i in  range(self.__usedEntries):
            entry = self.__entries[i]
            rv += entry.usedByProfile()
        return rv
    
    @property 
    def usedGC( self ):
        return self.rawUsedGC - self.usedByProfile()
        
                        
    def activeEntry(self):
        entry = self.currentSnap 
        ensure( entry is not None )
        sub = getattr( entry,'frame',None)
        if sub is not None:
            return sub.activeEntry()
        return entry
    

    def activeFrame(self) -> "ProfileFrameBase":
        entry = self.currentSnap 
        if entry is not None and entry.nest is not None and entry.nest is not self:
            return entry.nest.activeFrame()
        return self    
    
    def subFrame(self, context, name:str|None=None, name2:str|None=None) -> 'ProfileSubFrame':
        if name is not None:
            snap = self.activeFrame().snap(name, name2)
            return snap.subFrame(context,name2)
        return self.activeEntry().subFrame(context,name)

    def shouldProfileMemory(self):
        return False
        
    def reset(self ):
        nowNS = time.monotonic_ns()


        self.allocGc = gc.mem_alloc() if self.shouldProfileMemory() else 0
        self.rawUsedGC = 0
    
        self.__usedEntries = 0
        #self.__entries.clear()
        self.e = 0
        self.start = 0
        self.when = 0
        self.latestStartNS = self.priorStartNS = self.loopStartNS = nowNS
        self.currentSnap = None
        
    entries = property(lambda self: self.__usedEntries)
    
    def entry(self, index:int ):
        if index < 0 or index >= self.__usedEntries: return None
        return self.__entries[index]
        
    def __add( self, name:str, name2:str|None = None ): #, **kwds ):
        
        entry = ProfileFrameEntry.makeEntry( name, self.when, name2 )
        if self.__usedEntries < len(self.__entries):
            assert self.__entries[self.__usedEntries] is None
            self.__entries[self.__usedEntries] = entry 
        else:
            ensure( len(self.__entries) == self.__usedEntries )
            self.__entries.append( entry )

        if self.__usedEntries: 
            self.e = entry.lw

        self.__usedEntries += 1
        return entry

    
    def releaseNested(self):
        for i in  range(self.__usedEntries):
            entry = self.__entries[i]
            assert entry is not None
            self.__entries[i] = None
            entry.release()

    def snap(self, name:str, name2:str|None = None ) -> ProfileFrameEntry:
        self.priorStartNS = self.latestStartNS
        self.latestStartNS = time.monotonic_ns()
        self.when = ( self.latestStartNS - self.loopStartNS ) * 0.000000001
        priorEntry = self.currentSnap
        
        entry =  self.__add( name, name2 )
        self.currentSnap = entry
        if priorEntry is not None:
            priorEntry.e = entry.lw - priorEntry.lw
            if entry.shouldProfileMemory():
                priorEntry.rawUsedGC = entry.allocGc - priorEntry.allocGc 

        return entry
        
    def writeOn(self,config:ProfileWriteConfig,indent=''):
        return ProfilerRL.ProfileFrameBase_writeOn(self,config,indent)
        
    def jsonData(self,minF=None, minE = None, withSkipped=False, forceInclude = False, **kwds):
        minE = minE  if minE is not None else -1
        minF = minF or minE
        if self.e < minF and not forceInclude: return None
        
        skipped = []
        rvEntries=collections.OrderedDict()
        for snap in self.entries:
            if snap.e < minE: 
                skipped.append(snap.tag)
                continue
            rvEntries[snap.tag] =  snap.jsonData(**kwds)
            #rvEntries.append( [snap.tag, snap.jsonData(**kwds)] )
            
        rv = dict(
            e= self.e,
            entries=rvEntries,
            i=self.index,
            id=id(self)
        )
        if withSkipped:
            rv['skipped'] = skipped
        return rv
    
    def __str__(self):
        return f"PSF{('-'+self._name) if self._name is not None else ''}[{self.depth}:{self._rIndex}]@{id(self):X}"
    
    def finish(self):
        self.snap('end')
        
        if self.shouldProfileMemory():
            self.rawUsedGC =  gc.mem_alloc() - self.allocGc 
        
class ProfileSubFrame(ProfileFrameBase): 
    __context : 'LumensalisCP.Main.Updates.UpdateContext'
    
    def __init__(self, context:'LumensalisCP.Main.Updates.UpdateContext', name:str|None=None, name2:str|None=None):
        super().__init__()
        #self.__context = context
        #self._name = name
        #self.name2 = name2
        self._nextFree = None
        self.reset( context, name, name2 )
        
    def reset(self, context:'LumensalisCP.Main.Updates.UpdateContext', name:str|None=None, name2:str|None=None):
        super().reset()
        self.__context = context
        self._name = name
        self.name2 = name2
        
    def shouldProfileMemory(self):
        return gcm.PROFILE_MEMORY_NESTED
        
    def __enter__(self):
        try:
            context = self.__context
            ensure( context is not None and context.activeFrame is not None )
            self.__priorFrame = context.activeFrame
            self.depth = self.__priorFrame.depth + 1
            context.activeFrame = self
            # print( f"PSF ENTER {self} from {self.__priorFrame}" )
            
            self.snap('start')
        except Exception as inst:
            self.__context.main.dbgOut( "exception %r entering %r", inst, self )
        return self
    
    def __exit__(self,exc_type, exc_value, exc_tb):
        if exc_type is not None:
            print( f"PSF EXIT EXCEPTION {self} {exc_type} {exc_value} {exc_tb}" )
        try:
            self.finish()
            if self.__context.activeFrame is not self:
                print( f"PSF EXIT MISMATCH {self.__context.activeFrame} != {self} {exc_type} {exc_value} {exc_tb} {self.__context}" )
                print( f"  prior {self.__priorFrame} != {self} {exc_type} {exc_value} {exc_tb} {self.__context}" )
                frame = self.__context.baseFrame
                while frame is not None:
                    print( f"  - {frame}" )
                    frame = frame.nest()
            #else: print( f"PSF EXIT  {self}  to  {self.__priorFrame}" )

            self.__context.activeFrame = self.__priorFrame
        except Exception as inst:
            self.__context.main.dbgOut( "exception %r exiting %r", inst, self )
            
        return False
    
    

class ProfileFrame(ProfileFrameBase): 
    updateIndex: int
    start: TimeInSeconds
    eSleep: TimeInSeconds

    def __init__(self, *args, **kwds ):
        super().__init__()
        self.reset( *args, **kwds)
        
    def shouldProfileMemory(self):
        return gcm.PROFILE_MEMORY

    def reset(self, updateIndex =0, eSleep=0.0):
        # nowNS = time.monotonic_ns()

        self.updateIndex = updateIndex
        self.currentUpdateIndex = updateIndex
        self.eSleep = eSleep
        super().reset()
        
    def frameData(self,minF=None, minE = None, **kwds):
        minE = minE  if minE is not None else -1
        minF = minF or minE
        forceInclude = self.eSleep > min(minE,minF)
        
        baseData =super().jsonData(minF=minF, minE = minE, forceInclude=forceInclude, **kwds )
        if baseData is None: 
            return None
        return dict( i=self.updateIndex, eSleep=self.eSleep, **baseData )        

    def jsonData(self,minF=None, minE = None, **kwds):
        minE = minE  if minE is not None else -1
        minF = minF or minE
        forceInclude = self.eSleep > min(minE,minF)
        baseData =super().jsonData(minF=minF, minE = minE, forceInclude=forceInclude, **kwds )
        if baseData is None: 
            return None
        return dict( i=self.updateIndex, eSleep=self.eSleep, **baseData )

    def writeOn(self,config:ProfileWriteConfig,indent=''):
        return ProfilerRL.ProfileFrame_writeOn(self,config,indent)
    

class ProfileStubFrameEntry(ProfileFrameEntry): 
    def __init__(self,frame):
        super().__init__(tag="stub",when=0)

        self.__frame = frame
    def subFrame(self, context, name:str|None=None, name2:str|None=None) -> 'ProfileFrameBase':
        return self.__frame 

    def writeOn(self,target,indent='',**kwds):
        pass
    
    def jsonData(self,**kwds):
        rv = collections.OrderedDict(lw=self.lw, e=self.e, id=id(self), **self.etc)
        subFrame = self.nest
        return rv    
    
class ProfileStubFrame(ProfileFrame): 

    def __init__(self):
        super().__init__()
        self.when = 0
        self.updateIndex = -1
        self.__stubEntry = ProfileStubFrameEntry(self)
        
    def activeFrame(self) -> "ProfileFrameBase":
        return self

    def subFrame(self, context, name:str|None=None, name2:str|None=None) -> 'ProfileSubFrame':
        return self

    def snap(self, tag ) -> ProfileFrameEntry:
        return self.__stubEntry
        
    
    def reset(self, updateIndex =0, eSleep=0.0):
        pass
        
    def __enter__(self):
        return self
    
    def __exit__(self,exc_type, exc_value, exc_tb):
        pass
        return False
            

class Profiler(object):
    currentUpdateIndex: int
    when: TimeInSeconds
    currentSnap: ProfileFrameEntry | None
    timingsLength:int 
    timings: List[ProfileFrame]
    currentTiming: ProfileFrame
    disabled:bool
    
    def __init__(self, timings=None, stub=None ):
        if stub is None:
            stub = not _mlc.ENABLE_PROFILE
            
        if stub:
            self.timings = [ ProfileStubFrame() ]
            timings = 1
        else:
            timings = timings or 42
            self.timings = [ None for  _ in range(timings) ]
        
        self.timingsLength = timings
        self.disabled = stub
            
             
        self.nextNewFrame(0)
        
    def nextNewFrame(self, updateIndex, **kwds ) -> ProfileFrame: 
        if  self.disabled:
            return False
        timingIndex = updateIndex % self.timingsLength 
        old = self.timings[timingIndex]
        if old is not None:
            old.release()
        self.currentTiming = ProfileFrame.makeEntry( updateIndex, **kwds )
        self.timings[timingIndex] = self.currentTiming
        #self.currentTiming.reset( updateIndex, **kwds )
        return self.currentTiming
        
        #print( f"reset {updateIndex} {timingIndex} {self.currentTiming.updateIndex} {id(self.currentTiming)} ")
    
    def timingForUpdate( self, updateIndex ) -> ProfileFrame | None:
        if self.disabled: return self.timings[0]
        timingIndex = updateIndex % self.timingsLength
        rv = self.timings[timingIndex]
        if rv is not None and rv.updateIndex != updateIndex:
            print(f"tfy mismatch for {updateIndex} : [{timingIndex}].updateIndex={rv.updateIndex} {id(rv)}")
            return None
        return rv 
        

