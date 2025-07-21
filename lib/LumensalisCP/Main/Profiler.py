from __future__ import annotations

# pylint: disable=unused-import,import-error
#   pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

import time, collections
import gc # type: ignore

#import asyncio, wifi, displayio
#import busio, board

try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        pass
        
except ImportError:
    pass

import LumensalisCP.Main.Updates
from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
from LumensalisCP.util.kwCallback import KWCallback
from LumensalisCP.util.bags import Bag
from LumensalisCP.util.Releasable import Releasable
from . import ProfilerRL

from .PreMainConfig import pmc_gcManager, pmc_mainLoopControl

# pylint: disable=unused-argument, redefined-outer-name, attribute-defined-outside-init
# pylint: disable=protected-access, pointless-string-statement
TimePT = TimeInSeconds

getProfilerNow = time.monotonic
def ptToSeconds(v): return v

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
    _nest:ProfileSubFrame|None
    _nesting:  bool
    etc: Dict
    _nextSnap:ProfileSnapEntry|None

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
        return pmc_gcManager.PROFILE_MEMORY_ENTRIES
    
    def usedByProfile(self):
        if self.rawUsedGC:
            if self._nesting:
                assert self._nest is not None
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
        else: entry.reset( name, when, name2 ) # pylint: disable=no-member # type: ignore
        
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
    def nest( self ) -> ProfileSubFrame|None: return self._nest if self._nesting else None



    def subFrame(self, context, name:Optional[str]=None, name2:str|None = None) -> 'ProfileSubFrame':
        assert not self._nesting 
        self._nest = ProfileSubFrame.makeEntry(context,name, name2)
        self._nesting = True
        return self._nest

    def writeOn(self,config:ProfileWriteConfig,indent=''):
        return ProfilerRL.ProfileFrameEntry_writeOn(self,config,indent)
    
    def jsonData(self,**kwds) -> Mapping[str,Any]:
        #rv = collections.OrderedDict(lw=self.lw, e=self.e, id=id(self), **self.etc)
        rv:dict[str,Any] = dict(lw=self.lw, e=self.e, id=id(self), **self.etc)
        subFrame = self.nest
        if subFrame is not None:
            assert subFrame is not self
            #rv['nest'] = subFrame.jsonData() # **kwds)
        return rv

class IndexMap(object):
    def __init__(self, attrPrefix, tags  ):
        self.tags = tags
        self.indices:dict[str,int] = dict( [(tag,x) for x,tag in enumerate(tags)] )
        self.attrNames:dict[str,str] = dict( [(tag,attrPrefix+tag) for tag in tags] )
        
    def contains(self,tag):
        return self.indices.get(tag,None) is not None

    def attrFor(self,tag):
        return self.attrNames.get(tag,None)
    
class CachedList(object):
    def __init__(self, size ):
        self.__maxSize = size
        self.__size = 0
        self.__entries:list[Releasable|None] =  [None for _ in range(size)] 
        
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
            e = self.__entries[x]
            assert e is not None
            e.release()
            self.__entries[x] = None
        self.__size = 0
            
class ProfileFrameBase(Releasable): 
    
    gcFixedOverhead = 0
    #__entries:List[ProfileSnapEntry]
    #__usedEntries:int
    e:TimeSpanInSeconds
    when : TimeSpanInSeconds
    loopStartPT : TimePT
    priorStartPT: TimePT
    latestStartPT: TimePT
    firstSnap: ProfileSnapEntry|None
    currentSnap: ProfileSnapEntry|None
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
        #nowPT = time.monotonic_ns()
        nowPT = getProfilerNow()
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
        self.latestStartPT = self.priorStartPT = self.loopStartPT = nowPT
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
        # type: ignore
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
                    frame = frame.nest() # type: ignore
            #else: print( f"PSF EXIT  {self}  to  {self.__priorFrame}" )

            self.__context.activeFrame = self.__priorFrame
        except Exception as inst: # pylint: disable=broad-except
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
    
    def subFrame(self, context, name:Optional[str]=None, name2:Optional[str]=None) -> 'ProfileSubFrame':
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

    def releaseNested(self):
        if self.firstSnap is not None:
            self.firstSnap.release()
            self.firstSnap = None
            assert self.currentSnap is not None
            # assert not self.currentSnap._inUse
            self.currentSnap = None

    def _resetSnap(self,tag):
        snapTag = self.snapNames.attrFor( tag )
        assert snapTag is not None, f"Invalid snap tag {tag} in {self.snapNames}"
        existing:ProfileSnapEntry|None = getattr(self,snapTag,None)
        if existing is not None:
            existing.release()
        setattr(self,snapTag,None)
            
    def snap(self, name:str, name2:str|None = None, cls=ProfileSnapEntry ) -> ProfileSnapEntry:
        self.priorStartPT = self.latestStartPT
        self.latestStartPT = getProfilerNow()
        self.when = ptToSeconds ( self.latestStartPT - self.loopStartPT ) 
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
        
    """
    def jsonData(self,minF=None, minE = None, withSkipped=False, forceInclude = False, **kwds):
        # type: ignore
        # pylint: disable=no-member
        minE = minE  if minE is not None else -1
        minF = minF or minE
        if self.e < minF and not forceInclude: return None
        
        skipped = []
        rvEntries=collections.OrderedDict()
        for snap in self.entries: # type: ignore
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
            rv['skipped'] = skipped #type: ignore
        return rv
    """        
    def __str__(self):
        return f"PSF{('-'+self._name) if self._name is not None else ''}[{self.depth}:{self._rIndex}]@{id(self):X}"
    
    def finish(self):
        self.snap('end')
        
        if self.shouldProfileMemory():
            self.rawUsedGC =  gc.mem_alloc() - self.allocGc 
        
class ProfileSubFrame(ProfileFrameBase): 
    #__context : 'LumensalisCP.Main.Updates.UpdateContext'
    
    snapNames = IndexMap( 'snap', ['start','end' ] )
    
    def __init__(self, context:'LumensalisCP.Main.Updates.UpdateContext', name:Optional[str]=None, name2:Optional[str]=None):
        super().__init__(context)
        #self.__context = context
        #self._name = name
        #self.name2 = name2
        self._nextFree = None
        self.reset( context, name, name2 )
        
    def reset(self, context:'LumensalisCP.Main.Updates.UpdateContext', name:Optional[str]=None, name2:Optional[str]=None):
        super().reset(context)
        self._name = name
        self.name2 = name2
        
    @classmethod
    def makeEntry(cls,  context:'LumensalisCP.Main.Updates.UpdateContext', name:Optional[str]=None, name2:Optional[str]=None ):
        rp = cls.getReleasablePool()
        entry = cls._make_getFree( rp )

        if entry is None: entry = cls( context=context, name=name, name2=name2 )
        else: entry.reset( context=context, name=name, name2=name2 ) # pylint: disable=no-member # type: ignore
        
        return cls._makeFinish( rp, entry )
            
        
    def shouldProfileMemory(self):
        return pmc_gcManager.PROFILE_MEMORY_NESTED
        



class ProfileFrame(ProfileFrameBase): 
    updateIndex: int
    start: TimeInSeconds
    eSleep: TimeInSeconds
    
    snapNames = IndexMap( 'snap', ['start','timers', 'deferred','scenes','i2c', 'tasks','boards','end' ] )
    
    snapMaxEntries = 10
    
    def __init__(self,   context:'LumensalisCP.Main.Updates.UpdateContext',  eSleep=0.0):
        super().__init__(context)
        self.reset(  context, eSleep=eSleep)
        
    def shouldProfileMemory(self):
        return pmc_gcManager.PROFILE_MEMORY

    @classmethod
    def makeEntry(cls,   context:'LumensalisCP.Main.Updates.UpdateContext', eSleep=0.0):
        """ NASTY!!! 
            the only reason this is overridden is to eliminate the cost of the 
            temporaries for *args and **kwds in CircuitPython GC
        """
        rp = cls.getReleasablePool()
        entry = cls._make_getFree( rp )

        if entry is None: entry = cls( context, eSleep=eSleep )
        else: entry.reset( context, eSleep=eSleep ) # pylint: disable=no-member # type: ignore
        
        return cls._makeFinish( rp, entry )
    
    def reset(self, context:'LumensalisCP.Main.Updates.UpdateContext',  eSleep=0.0):
        # nowPT = time.monotonic_ns()

        #self.currentUpdateIndex = 
        self.updateIndex = context.updateIndex
        self.eSleep = eSleep
        super().reset(context)
        

        
    def frameData(self,minF=None, minE = None, **kwds):
        minE = minE  if minE is not None else -1
        minF = minF or minE
        #forceInclude = self.eSleep > min(minE,minF)
        
        baseData = {} # super().jsonData(minF=minF, minE = minE, forceInclude=forceInclude, **kwds )
        if baseData is None: 
            return None
        return dict( i=self.updateIndex, eSleep=self.eSleep, **baseData )        

    """
    def jsonData(self,minF=None, minE = None, **kwds): # type: ignore
        minE = minE  if minE is not None else -1
        minF = minF or minE
        forceInclude = self.eSleep > min(minE,minF)
        baseData =super().jsonData(minF=minF, minE = minE, forceInclude=forceInclude, **kwds )
        if baseData is None: 
            return None
        return dict( i=self.updateIndex, eSleep=self.eSleep, **baseData )
"""

    def writeOn(self,config:ProfileWriteConfig,indent=''):
        return ProfilerRL.ProfileFrame_writeOn(self,config,indent)
    

class ProfileStubFrameEntry(ProfileSnapEntry): 
    def __init__(self,frame=None):
        super().__init__(tag="stub",when=0)
        self.__frame = frame
        
    def subFrame(self, context, name:Optional[str]=None, name2:Optional[str]=None) -> 'ProfileFrameBase': # type: ignore
        return self.__frame  # type: ignore

    def writeOn(self,config:ProfileWriteConfig,indent=''):
        pass
    
    def jsonData(self,**kwds):
        rv = collections.OrderedDict(lw=self.lw, e=self.e, id=id(self), **self.etc)
        return rv    
    
class ProfileStubFrame(ProfileFrame): 

    def __init__(self, context:'LumensalisCP.Main.Updates.UpdateContext'):
        super().__init__(context=context, eSleep=0.0)
        self.when = 0
        self.updateIndex = -1
        self.__stubEntry = ProfileStubFrameEntry(self)
        
    def activeFrame(self) -> "ProfileFrameBase":
        return self

    def subFrame(self, context, name:Optional[str]=None, name2:Optional[str]=None) -> 'ProfileSubFrame':
        return self # type: ignore

    def snap(self, name:str, name2:str|None = None, cls=ProfileSnapEntry ) -> ProfileSnapEntry:
        return self.__stubEntry
        
    
    def reset(self, context:'LumensalisCP.Main.Updates.UpdateContext',  eSleep=0.0):
        pass
        
    def __enter__(self):
        return self
    
    def __exit__(self,exc_type, exc_value, exc_tb):
        return False

#############################################################################

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
            stub = not pmc_mainLoopControl.ENABLE_PROFILE
            
        self.stubFrame = ProfileStubFrame(context)
        self._preContextIndex = context.updateIndex
        if stub:
            self.timings = [ self.stubFrame ]
            timings = 1
        else:
            timings = timings or pmc_mainLoopControl.profileTimings
            self.timings = [ ProfileFrame.makeEntry(context,0) for  _ in range(timings) ]
        
        self.timingsLength = timings
        self.disabled = stub
            
             
        #self.nextNewFrame(0)
        
    def nextNewFrame(self, context:'LumensalisCP.Main.Updates.UpdateContext', eSleep:TimeInSeconds=0 ) -> ProfileFrame: 
        assert not self.disabled
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
