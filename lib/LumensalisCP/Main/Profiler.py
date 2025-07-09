
import LumensalisCP.Main.Updates
from LumensalisCP.Main._preMainConfig import _mlc
import time, math, asyncio, traceback, os, gc, wifi, displayio
import busio, board
import collections

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
from LumensalisCP.util.kwCallback import KWCallback
from LumensalisCP.util.bags import Bag
from . import ProfilerRL
from .Releasable import *
from ._preMainConfig import gcm, _mlc
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
        

class ProfileSnapEntry(Releasable): 
    # __slots__ = ["name","name2","lw","e","_nest","_nesting","etc"]
    __defaultEtc = {}
    
    gcFixedOverhead = 0
    
    name:str
    name2:str|None
    lw: TimeSpanInSeconds
    e: TimeSpanInSeconds
    _nest:  "ProfileSubFrame"|None
    _nesting:  bool
    etc: Dict
    _nextSnap: "ProfileSnapEntry"

    def __init__(self,tag:str, when:TimeInSeconds, name2:str|None = None):
        super().__init__()
        self._nextSnap = None
        self.reset(tag,when, name2)

    def releaseNested(self):
        #print( f"releaseNested snap {self} @{id(self)}" )
        if self._nesting:
            assert self._nest is not None
            nest = self._nest
            self._nest = None
            self._nesting = False
            nest.release()
        
        if self._nextSnap is not None:
            #print( f"  releasing next {id(self._nextSnap)}" )
            self._nextSnap.release()
            self._nextSnap = None

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

    @classmethod
    def makeEntry(cls, name:str, when:TimeInSeconds, name2:str|None = None ):
        rp = cls.getReleasablePool()
        entry = cls._make_getFree( rp )

        if entry is None: entry = cls(name, when, name2)
        else: entry.reset( name, when, name2 )
        
        return cls._makeFinish( rp, entry )
            
    def reset( self, name:str, when:TimeInSeconds, name2:str|None = None ):
        self.name = name
        self.lw = when
        self.e = 0.0
        self.etc = self.__defaultEtc
        self._nesting = False
        self.allocGc = gc.mem_alloc() if self.shouldProfileMemory() else 0
            
        self.rawUsedGC = 0
        self.name2 = name2

        
    def augment( self, tag:str,val ):
        if self.etc is self.__defaultEtc:
            self.etc = {}
        self.etc[tag] = val
        
    @property 
    def nest( self ) -> "ProfileSubFrame"|None: return self._nest if self._nesting else None



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

class IndexMap(object):
    def __init__(self, attrPrefix, tags  ):
        self.tags = tags
        self.indices = dict( [(tag,x) for x,tag in enumerate(tags)] )
        self.attrNames = dict( [(tag,attrPrefix+tag) for tag in tags] )
        
    def contains(self,tag):
        return self.indices.get(tag,None) is not None

    def contains(self,tag):
        return self.indices.get(tag,None) is not None
    
    def attrFor(self,tag):
        return self.attrNames.get(tag,None)
    
class CachedList(object):
    def __init__(self, size ):
        self.__maxSize = size
        self.__size = 0
        self.__entries = [None for _ in range(size)] 
        
    def __len__( self ):
        return self.__size
    def __getitem__(self,x):
        assert x >= 0 and x < self.__size
        return self.__entries[x]
    
    def append( self, item:Releasable ):
        assert self.__size < self.__maxSize
        assert item is not None
        self.__entries[self.__size] = item
        self.__size += 1
        
    def reset( self ):
        for x in range(self.__size):
            self.__entries[x].release()
            self.__entries[x] = None
        self.__size = 0
            
class ProfileFrameBase(Releasable): 
    #__entries:List[ProfileSnapEntry]
    #__usedEntries:int
    e:TimeSpanInSeconds
    when : TimeSpanInSeconds
    loopStartNS : int
    priorStartNS: int
    latestStartNS: int
    firstSnap: ProfileSnapEntry
    currentSnap: ProfileSnapEntry
    currentSnapIndex: int
    index: int
    depth: int = 0
    
    snapNames: ClassVar[IndexMap]
    snapMaxEntries: ClassVar[int]
    
    nextFrameIndex = 1

    snapMaxEntries = 2
    #gcFixedOverhead = 112
    
    #_resets = 0
    #_allocs = 0
    
    def __init__(self, context:'LumensalisCP.Main.Updates.UpdateContext'):
        super().__init__()
        #self.__entries = []
        self.firstSnap = None
        self.currentSnap = None
        self._name = '--'
        #self.__usedEntries = 0
        self.__context = context

        #ProfileFrameBase._allocs += 1
        #self.reset()
        
        
    def reset(self, context:'LumensalisCP.Main.Updates.UpdateContext' ):
        nowNS = time.monotonic_ns()
        assert isinstance(context,LumensalisCP.Main.Updates.UpdateContext)
        self.__context = context
        self.allocGc = gc.mem_alloc() if self.shouldProfileMemory() else 0
        self.rawUsedGC = 0
        assert self.firstSnap is None
        assert self.currentSnap is None
        assert not self._inUse
        #if self.firstSnap is not None:
        #    self.firstSnap.release()
        self.firstSnap = None
        #self.__usedEntries = 0
        #self.__entries.clear()
        self.e = 0
        self.start = 0
        self.when = 0
        self.latestStartNS = self.priorStartNS = self.loopStartNS = nowNS
        self.currentSnap = None
        self.currentSnapIndex = 0

        #for tag in self.snapNames.attrNames:
        #    self._resetSnap(tag)
                            
    def __enter__(self) -> "ProfileFrameBase":
        try:
            context = self.__context
            ensure( context is not None and 
                   ((context.activeFrame is not None)
                    or self.__class__ is ProfileFrame
                   )
                   )
            self.__priorFrame = context.activeFrame
            self.depth = self.__priorFrame.depth + 1
            context.activeFrame = self
            # print( f"PSF ENTER {self} from {self.__priorFrame}" )
            
            self.snap('start')
        except Exception as inst:
            SHOW_EXCEPTION(inst, "ProfileFrame entering %r",self )
            raise
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
            SHOW_EXCEPTION(inst, "ProfileFrame exiting %r",self )
            
        return False
    
    def usedByProfile(self):
        rv = self.gcFixedOverhead
        #for i in  range(self.__usedEntries):
        #    entry = self.__entries[i]
        for entry in self.iterSnaps():
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
            #snap = self.activeFrame().snap(name, name2)
            snap = self.snap(name, name2)
            #snap = self.activeFrame().snap(name, name2)
            return snap.subFrame(context,name, name2)
        #return self.activeEntry().subFrame(context,name,name2)
        return self.subFrame(context,name,name2)

    def shouldProfileMemory(self):
        return False

        
    #entries = property(lambda self: self.__usedEntries)
    
    def iterSnaps(self) -> Generator[ProfileSnapEntry]:
        return ProfilerRL.ProfileFrameBase_iterSnaps(self) 

    #def entry(self, index:int ):
    #    if index < 0 or index >= self.__usedEntries: return None
    #    return self.__entries[index]
        
    def __add( self, cls, name:str, name2:str|None = None ): #, **kwds ):
        
        entry = cls.makeEntry( name, self.when, name2 )
        
        entry.snapIndex = self.currentSnapIndex
        self.currentSnapIndex += 1
        attrName = self.snapNames.attrFor(name)
        if attrName is not None:
            setattr(self,attrName,entry)
        else:
            if self.__usedEntries < len(self.__entries):
                assert self.__entries[self.__usedEntries] is None
                self.__entries[self.__usedEntries] = entry 
            else:
                ensure( len(self.__entries) == self.__usedEntries )
                self.__entries.append( entry )
            self.__usedEntries += 1

        if self.currentSnapIndex: 
            self.e = entry.lw
        

        return entry

    
    def releaseNested(self):
        if True:
            if self.firstSnap is not None:
                self.firstSnap.release()
                self.firstSnap = None
                assert self.currentSnap is not None
                # assert not self.currentSnap._inUse
                self.currentSnap = None
        else:
            for i in  range(self.__usedEntries):
                entry = self.__entries[i]
                assert entry is not None
                self.__entries[i] = None
                entry.release()
            self.__usedEntries = 0

            for tag in self.snapNames.tags:
                self._resetSnap(tag)
                
    def _resetSnap(self,tag):
        snapTag = self.snapNames.attrFor( tag )
        existing:ProfileSnapEntry = getattr(self,snapTag,None)
        if existing is not None:
            existing.release()
        setattr(self,snapTag,None)
            
    def snap(self, name:str, name2:str|None = None, cls=ProfileSnapEntry ) -> ProfileSnapEntry:
        self.priorStartNS = self.latestStartNS
        self.latestStartNS = time.monotonic_ns()
        self.when = ( self.latestStartNS - self.loopStartNS ) * 0.000000001
        priorEntry = self.currentSnap
        
        entry = cls.makeEntry( name, self.when, name2 )
        
        #entry.snapIndex = self.currentSnapIndex
        #self.currentSnapIndex += 1
        #entry =  self.__add( cls, name, name2 )
        self.currentSnap = entry
        if priorEntry is not None:
            priorEntry.e = entry.lw - priorEntry.lw
            priorEntry._nextSnap = entry
            if entry.shouldProfileMemory():
                priorEntry.rawUsedGC = entry.allocGc - priorEntry.allocGc 
        else:
            assert self.firstSnap is None
            self.firstSnap = entry

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
    #__context : 'LumensalisCP.Main.Updates.UpdateContext'
    
    snapNames = IndexMap( 'snap', ['start','end' ] )
    
    def __init__(self, context:'LumensalisCP.Main.Updates.UpdateContext', name:str|None=None, name2:str|None=None):
        super().__init__(context)
        #self.__context = context
        #self._name = name
        #self.name2 = name2
        self._nextFree = None
        self.reset( context, name, name2 )
        
    def reset(self, context:'LumensalisCP.Main.Updates.UpdateContext', name:str|None=None, name2:str|None=None):
        super().reset(context)
        self._name = name
        self.name2 = name2
        
    @classmethod
    def makeEntry(cls,  context:'LumensalisCP.Main.Updates.UpdateContext', name:str|None=None, name2:str|None=None ):
        rp = cls.getReleasablePool()
        entry = cls._make_getFree( rp )

        if entry is None: entry = cls( context=context, name=name, name2=name2 )
        else: entry.reset( context=context, name=name, name2=name2 )
        
        return cls._makeFinish( rp, entry )
            
        
    def shouldProfileMemory(self):
        return gcm.PROFILE_MEMORY_NESTED
        



class ProfileFrame(ProfileFrameBase): 
    updateIndex: int
    start: TimeInSeconds
    eSleep: TimeInSeconds
    
    snapNames = IndexMap( 'snap', ['start','timers', 'deferred','scenes','i2c', 'tasks','boards','end' ] )
    
    snapMaxEntries = 10
    
    def __init__(self,   context:'LumensalisCP.Main.Updates.UpdateContext'=None,  eSleep=0.0):
        super().__init__(context)
        self.reset(  context, eSleep=eSleep)
        
    def shouldProfileMemory(self):
        return gcm.PROFILE_MEMORY

    @classmethod
    def makeEntry(cls,   context:'LumensalisCP.Main.Updates.UpdateContext', eSleep=0.0):
        """ NASTY!!! 
            the only reason this is overridden is to eliminate the cost of the 
            temporaries for *args and **kwds in CircuitPython GC
        """
        rp = cls.getReleasablePool()
        entry = cls._make_getFree( rp )

        if entry is None: entry = cls( context, eSleep=eSleep )
        else: entry.reset( context, eSleep=eSleep )
        
        return cls._makeFinish( rp, entry )
    
    def reset(self, context:'LumensalisCP.Main.Updates.UpdateContext'=None,  eSleep=0.0):
        # nowNS = time.monotonic_ns()

        #self.currentUpdateIndex = 
        self.updateIndex = context.updateIndex
        self.eSleep = eSleep
        super().reset(context)
        

        
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
    

class ProfileStubFrameEntry(ProfileSnapEntry): 
    def __init__(self,frame=None):
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

    def __init__(self, context=None):
        super().__init__(context=None, eSleep=0.0)
        self.when = 0
        self.updateIndex = -1
        self.__stubEntry = ProfileStubFrameEntry(self)
        
    def activeFrame(self) -> "ProfileFrameBase":
        return self

    def subFrame(self, context, name:str|None=None, name2:str|None=None) -> 'ProfileSubFrame':
        return self

    def snap(self, tag, tag2=None ) -> ProfileSnapEntry:
        return self.__stubEntry
        
    
    def reset(self, context=None, updateIndex =0, eSleep=0.0):
        pass
        
    def __enter__(self):
        return self
    
    def __exit__(self,exc_type, exc_value, exc_tb):
        pass
        return False
            

class Profiler(object):
    updateIndex: int
    when: TimeInSeconds
    currentSnap: ProfileSnapEntry | None
    timingsLength:int 
    timings: List[ProfileFrame]
    currentTiming: ProfileFrame
    disabled:bool
    stubFrame:ProfileStubFrame
    
    def __init__(self, context:'LumensalisCP.Main.Updates.UpdateContext', timings=None, stub=None ):
        if stub is None:
            stub = not _mlc.ENABLE_PROFILE
            
        self.stubFrame = ProfileStubFrame(context)
        self._preContextIndex = context.updateIndex
        if stub:
            self.timings = [ self.stubFrame ]
            timings = 1
        else:
            timings = timings or _mlc.profileTimings
            self.timings = [ ProfileFrame.makeEntry(context,0) for  _ in range(timings) ]
        
        self.timingsLength = timings
        self.disabled = stub
            
             
        #self.nextNewFrame(0)
        
    def nextNewFrame(self, context:'LumensalisCP.Main.Updates.UpdateContext', eSleep=0 ) -> ProfileFrame: 
        if  self.disabled:
            return False
        updateIndex = context.updateIndex
        timingIndex = updateIndex % self.timingsLength 
        old = self.timings[timingIndex]
        if old is not None:
            old.release()
        self.currentTiming = ProfileFrame.makeEntry( context, eSleep=eSleep )
        self.timings[timingIndex] = self.currentTiming
        #self.currentTiming.reset( updateIndex, **kwds )
        return self.currentTiming
        
        #print( f"reset {updateIndex} {timingIndex} {self.currentTiming.updateIndex} {id(self.currentTiming)} ")
    
    def timingForUpdate( self, updateIndex ) -> ProfileFrame | None:
        if self.disabled: return self.timings[0]
        timingIndex = updateIndex % self.timingsLength
        rv = self.timings[timingIndex]
        if rv is not None and rv.updateIndex != updateIndex:
            if rv.updateIndex != self._preContextIndex:
                print(f"tfy mismatch for {updateIndex} : [{timingIndex}].updateIndex={rv.updateIndex} {id(rv)}")
            return None
        return rv 
        

