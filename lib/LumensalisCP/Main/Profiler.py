from __future__ import annotations

# pylint: disable=unused-import,import-error
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false
# pyright: reportPrivateUsage=false

import time
from collections import OrderedDict
import gc 

try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from LumensalisCP.Main.Updates import UpdateContext

except ImportError:
    pass

from LumensalisCP.Main.PreMainConfig import ImportProfiler
_sayProfilerImport = ImportProfiler( "Profiler" )

import LumensalisCP.Main.Updates
from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
from LumensalisCP.util.kwCallback import KWCallback, KWCallbackArg
from LumensalisCP.util.bags import Bag
from LumensalisCP.util.Releasable import Releasable
from LumensalisCP.Main import ProfilerRL

from LumensalisCP.Main.PreMainConfig import pmc_gcManager, pmc_mainLoopControl

_sayProfilerImport.parsing()

# pylint: disable=unused-argument, redefined-outer-name, attribute-defined-outside-init
# pylint: disable=protected-access, pointless-string-statement
TimePT = TimeInSeconds

getProfilerNow:Callable[[],TimePT] = time.monotonic # type: ignore[reportUnknownVariableType]

def ptToSeconds(v: TimePT|float) -> TimeInSeconds:
    return TimeInSeconds(v)

PWJsonNestDataType:TypeAlias = Union[StrAnyDict,List[Any]]

class ProfileWriteConfig(object):
    
    def __init__(self,target:TextIO|list[str]|StrAnyDict|None = None,
                 minE:Optional[float]=None,minEB:Optional[int]=None,
                 minF:Optional[float]=None,minSubF:Optional[float]=None,
                 minB:Optional[int]=None,
                 showMemory:Optional[bool]=None,
                 showMemoryEntries:Optional[bool]=None,
                   **kwds:StrAnyDict) ->None:
 
        self.target:Any = None
        self.minB:int = minB if minB is not None else 1024
        self.minEB:int = minEB if minEB is not None else self.minB
        self.minE:float = minE if minE is not None else -1
        self.minF:float =  minF or self.minE 
        self.minSubF:float = minSubF or 0
        if showMemory is None: showMemory = pmc_gcManager.PROFILE_MEMORY
        if showMemoryEntries is None: showMemoryEntries = pmc_gcManager.PROFILE_MEMORY_ENTRIES
        self.showMemory:bool = showMemory
        self.showMemoryEntries:bool = showMemoryEntries 

        self.__target = target
        self.__makingJson = isinstance(target, (dict, OrderedDict, list))
        self.__jsonData:PWJsonNestDataType|None = target if self.__makingJson else None # type:ignore[reportUnknownVariableType]
        self.__jsonNestDataStack:list[PWJsonNestDataType] = [self.__jsonData] if self.__jsonData is not None else []
        self.__jsonNestData:PWJsonNestDataType|None = None
        self.__jsonNestTag:str|None = None

    def __repr__(self):
        return f"mE={self.minE} mF={self.minF} mSF={self.minSubF} mB={self.minB} mEB={self.minEB}"


    def tooMuchMemoryUsed( self:ProfileWriteConfig ,
                entry:ProfileSnapEntry|ProfileFrameBase,
            ) -> bool:
        if isinstance(entry,ProfileSnapEntry):
            return entry.usedGC >= self.minEB
        return entry.usedGC >= self.minB 

    def shouldShowSnap(self, snap:ProfileSnapEntry) -> bool:
        return (snap.e >= self.minE) or self.tooMuchMemoryUsed(snap)


    def shouldShowFrame(self, frame:ProfileFrameBase) -> bool:
        if isinstance(frame,ProfileFrame):
            return ( frame.eSleep > min(self.minE,self.minF) ) or ( frame.e >= self.minF )

        return self.tooMuchMemoryUsed( frame ) or ( frame.e >= self.minSubF )

    @property
    def makingJson(self) -> bool:
        return self.__makingJson
    
    @property
    def top(self) -> PWJsonNestDataType:
        assert len(self.__jsonNestDataStack) > 0, f"top len() < 1 for {self.__jsonNestDataStack}"
        return self.__jsonNestDataStack[-1]

    @property
    def topDict(self) -> StrAnyDict:
        rv = self.top
        assert isinstance(rv,(dict,OrderedDict)), f"top {rv} is not a dict, but {type(rv)}"
        return rv

    def nest( self, data:PWJsonNestDataType, tag:Optional[str] = None ) -> Self:
        assert len(self.__jsonNestDataStack) > 0
        top = self.__jsonNestDataStack[-1]
        if isinstance(top, (dict,OrderedDict)):
            assert tag is not None, f"Cannot nest data {data} without tag in {top}"
            top[tag] = data
        else:
            assert  isinstance(top, list)
            top.append(data)
        self.__jsonNestData = data    

        return self

    def nestList( self, tag:Optional[str] = None ) -> Self:
        return self.nest( [], tag=tag )

    def nestDict( self, tag:Optional[str] = None ) -> Self:
        return self.nest( OrderedDict(), tag=tag )

    def __enter__(self) -> ProfileWriteConfig:
        if self.__makingJson:
            assert self.__jsonNestData is not None
            self.__jsonNestDataStack.append( self.__jsonNestData )

        return self
    def __exit__(self, exc_type:Optional[Type[BaseException]], exc_value:Optional[BaseException], exc_tb:Optional[Any]) -> None:

        if self.__makingJson:
            top = self.__jsonNestDataStack.pop() # type:ignore[reportUnknownVariableType]
    
    def writeLine( self, fmt:str, *args:Any ) -> None:
        message = safeFmt( fmt, *args )
        if isinstance(self.__target, list):
            self.__target.append( message )
        else:
            # assert isinstance(self.__target, TextIO), f"Invalid target {self.__target} for ProfileWriteConfig"
            self.__target.write( message ) # type: ignore[reportAttributeAccessIssue]
            self.__target.write( "\r\n" ) # type: ignore[reportAttributeAccessIssue]

class ProfileSnapEntry(Releasable): 
    # __slots__ = ["name","name2","lw","e","_nest","_nesting","etc"]
    __defaultEtc: dict[str, Any] = {}
    
    gcFixedOverhead = 0
    
    name:str
    name2:str|None
    lw: TimePT
    e: TimeSpanInSeconds
    _nest:ProfileSubFrame|None
    _nesting:  bool
    etc: dict[str, Any]
    _nextSnap:ProfileSnapEntry|None

    def __init__(self ) -> None:
       #tag:str, when:TimeInSeconds, name2:str|None = None):
        super().__init__()
        self._nextSnap = None
        #self.reset(tag,when, name2)


    def releaseNested(self):
        #print( f"releaseNested snap {self} @{id(self)}" )
        if self._nesting:
            assert self._nest is not None
            nest = self._nest
            self._nest = None
            self._nesting = False
            assert nest is not self, f"releasing nested {nest} != {self}"
            nest.release()
        
        assert self._nextSnap is None
        if self._nextSnap is not None:
            #print( f"  releasing next {id(self._nextSnap)}" )
            assert self._nextSnap is not self, f"releasing next {self._nextSnap} != {self}"
            snap = self._nextSnap
            self._nextSnap = None
            snap.release()

    def shouldProfileMemory(self) -> bool:
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

        if entry is None: entry = cls()
        entry.reset( name, when, name2 ) # pylint: disable=no-member # type: ignore
        
        return cls._makeFinish( rp, entry )
            
    def reset( self, name:str, when:TimePT, name2:str|None = None ):
        self.name = name
        self.lw = when
        self.e:float = 0.0
        self.etc = self.__defaultEtc
        self._nesting = False
        self.allocGc = gc.mem_alloc() if self.shouldProfileMemory() else 0
            
        self.rawUsedGC = 0
        self.name2 = name2

        
    def augment( self, tag:str,val:Any ):
        if self.etc is self.__defaultEtc:
            self.etc = {}
        self.etc[tag] = val
        
    @property 
    def nest( self ) -> ProfileSubFrame|None: return self._nest if self._nesting else None



    def subFrame(self, context:UpdateContext, 
                 name:Optional[str]=None, 
                 name2:str|None = None
            ) -> 'ProfileSubFrame':
        assert not self._nesting 
        self._nest = ProfileSubFrame.makeEntry(context,name, name2)
        self._nesting = True
        return self._nest

    def writeOn(self,config:ProfileWriteConfig,indent:str=''):
        return ProfilerRL.ProfileSnapEntry_writeOn(self,config,indent)
    
    def jsonData(self,**kwds:StrAnyDict) -> Mapping[str,Any]:
        #rv = collections.OrderedDict(lw=self.lw, e=self.e, id=id(self), **self.etc)
        rv:dict[str,Any] = dict(lw=self.lw, e=self.e, id=id(self), **self.etc)
        subFrame = self.nest
        if subFrame is not None:
            assert subFrame is not self
            #rv['nest'] = subFrame.jsonData() # **kwds)
        return rv

class IndexMap(object):
    def __init__(self, attrPrefix:str, tags:list[str] ):
        self.tags = tags
        self.indices:dict[str,int] = dict( [(tag,x) for x,tag in enumerate(tags)] )
        self.attrNames:dict[str,str] = dict( [(tag,attrPrefix+tag) for tag in tags] )
        
    def contains(self,tag:str) -> bool:
        return self.indices.get(tag,None) is not None

    def attrFor(self,tag:str) -> str|None:
        return self.attrNames.get(tag,None)
    
class CachedList(object):
    def __init__(self, size:int ):
        self.__maxSize = size
        self.__size = 0
        self.__entries:list[Releasable|None] =  [None for _ in range(size)] 
        
    def __len__( self ) -> int:
        return self.__size
    
    def __getitem__(self,x:int) -> Releasable|None:
        assert x >= 0 and x < self.__size
        return self.__entries[x]
    
    def append( self, item:Releasable ) -> None:
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
    frameStartPT : TimePT
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
    
    def __init__(self):
        super().__init__()
        #self.__entries = []
        self.firstSnap = None
        self.currentSnap = None
        self._name = '--'
        #self.__usedEntries = 0
        #self.__context = context

        #ProfileFrameBase._allocs += 1
        #self.reset()
        
    @property
    def name(self) -> str|None:
        return self._name
        
    def reset(self, context:UpdateContext ) -> None:
        #nowPT = time.monotonic_ns()
        nowPT = getProfilerNow()
        #assert isinstance(context,UpdateContext)
        self.__context:UpdateContext = context
        self.allocGc:int = gc.mem_alloc() if self.shouldProfileMemory() else 0
        self.rawUsedGC:int = 0
        assert self.firstSnap is None
        assert self.currentSnap is None
        assert not self._inUse
        #if self.firstSnap is not None:
        #    self.firstSnap.release()
        self.firstSnap:ProfileSnapEntry|None = None
        #self.__usedEntries = 0
        #self.__entries.clear()
        self.e:float = 0
        self.start:float = 0
        self.when:float = 0
        self.latestStartPT:TimePT = nowPT
        self.priorStartPT:TimePT = nowPT
        self.frameStartPT:TimePT = nowPT
        self.frameEndPT:TimePT = nowPT

        self.currentSnap:ProfileSnapEntry|None = None
        self.currentSnapIndex:int= 0

        #for tag in self.snapNames.attrNames:
        #    self._resetSnap(tag)
                            
    def __enter__(self) -> ProfileFrameBase:
        try:
            context = self.__context
            assert context is not None 
            assert ((context.activeFrame is not None) or self.__class__ is ProfileFrame)
                   
            self.__priorFrame = context.activeFrame
            self.depth = self.__priorFrame.depth + 1
            context.activeFrame = self
            # print( f"PSF ENTER {self} from {self.__priorFrame}" )
            
            self.snap('start')
        except Exception as inst:
            SHOW_EXCEPTION(inst, "ProfileFrame entering %r",self )
            raise
        return self

    def __exit__(self,exc_type:Optional[Type[BaseException]], exc_value:Optional[BaseException], exc_tb:Optional[Any]):
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
    
    def subFrame(self, context:UpdateContext, name:Optional[str]=None, name2:Optional[str]=None) -> 'ProfileSubFrame':
        if name is not None:
            #snap = self.activeFrame().snap(name, name2)
            snap = self.snap(name, name2)
            #snap = self.activeFrame().snap(name, name2)
            return snap.subFrame(context,name, name2)
        #return self.activeEntry().subFrame(context,name,name2)
        return self.subFrame(context,name,name2)

    def shouldProfileMemory(self) -> bool:
        return False

        
    #entries = property(lambda self: self.__usedEntries)
    
    def iterSnaps(self) -> Generator[ProfileSnapEntry]:
        return ProfilerRL.ProfileFrameBase_iterSnaps(self) 

    def releaseNested(self):
        snap = self.firstSnap
        if snap is not None:
            assert self.currentSnap is not None
            # assert not self.currentSnap._inUse
            self.currentSnap = None
            self.firstSnap = None
            while snap is not None:
                nextSnap = snap._nextSnap
                snap._nextSnap = None
                snap.release()
                snap = nextSnap
                
        
    def _resetSnap(self,tag:str):
        snapTag = self.snapNames.attrFor( tag )
        assert snapTag is not None, f"Invalid snap tag {tag} in {self.snapNames}"
        existing:ProfileSnapEntry|None = getattr(self,snapTag,None)
        if existing is not None:
            existing.release()
        setattr(self,snapTag,None)
            
    def snap(self, name:str, name2:str|None = None, cls:type=ProfileSnapEntry ) -> ProfileSnapEntry:
        self.priorStartPT = self.latestStartPT
        self.latestStartPT = getProfilerNow()
        self.when = ptToSeconds ( self.latestStartPT - self.frameStartPT ) 
        priorEntry = self.currentSnap
        
        
        entry:ProfileSnapEntry = cls.makeEntry( name, self.when, name2 ) # type:ignore[reportCallIssue]
        assert isinstance( entry, ProfileSnapEntry ), f"Invalid snap entry {entry} for {name} in {self.snapNames}"
        #entry.snapIndex = self.currentSnapIndex
        #self.currentSnapIndex += 1
        #entry =  self.__add( cls, name, name2 )
        self.currentSnap = entry
        if priorEntry is not None:
            priorEntry.e = entry.lw - priorEntry.lw
            priorEntry._nextSnap = entry # type:ignore[reportAttributeAccessIssue]
            if entry.shouldProfileMemory():
                priorEntry.rawUsedGC = entry.allocGc - priorEntry.allocGc 
        else:
            assert self.firstSnap is None
            self.firstSnap = entry

        return entry
        
    def writeOn(self,config:ProfileWriteConfig,indent:str=''):
        return ProfilerRL.ProfileFrameBase_writeOn(self,config,indent)
    
    def __str__(self):
        return f"PSF{('-'+self.name) if self.name is not None else ''}[{self.depth}:{self._rIndex}]@{id(self):X}"
    
    def finish(self):
        snap = self.snap('end')
        self.frameEndPT = getProfilerNow()
        #snap.e = getProfilerNow() - self.latestStartPT
        self.e = self.frameEndPT - self.frameStartPT 
        
        if self.shouldProfileMemory():
            self.rawUsedGC =  gc.mem_alloc() - self.allocGc 
        
class ProfileSubFrame(ProfileFrameBase): 
    #__context : UpdateContext
    
    snapNames = IndexMap( 'snap', ['start','end' ] )
    
    def __init__(self, ): # context:UpdateContext, name:Optional[str]=None, name2:Optional[str]=None):
        super().__init__()#context)
        #self.__context = context
        #self._name = name
        #self.name2 = name2
        self._nextFree = None
        #self.reset( context, name, name2 )
        
    def reset(self, context:UpdateContext, name:Optional[str]=None, name2:Optional[str]=None):
        super().reset(context)
        self._name = name
        self.name2 = name2
        
    @classmethod
    def makeEntry(cls,  context:UpdateContext,
                   name:Optional[str]=None, name2:Optional[str]=None 
                ) -> Self:
    
        rp = cls.getReleasablePool()
        entry = cls._make_getFree( rp )

        if entry is None: entry = cls( )
        entry.reset( context=context, name=name, name2=name2 ) # pylint: disable=no-member # type: ignore
        
        return cls._makeFinish( rp, entry )
            
        
    def shouldProfileMemory(self) -> bool:
        return pmc_gcManager.PROFILE_MEMORY_NESTED


class ProfileFrame(ProfileFrameBase): 
    updateIndex: int
    #start: TimeInSeconds
    eSleep: TimeSpanInSeconds
    
    snapNames = IndexMap( 'snap', ['start','timers', 'deferred','scenes','i2c', 'tasks','boards','end' ] )
    
    snapMaxEntries = 10
    
    def __init__(self ) -> None:
         #,   context:UpdateContext,  eSleep:TimeSpanInSeconds=0.0):
        super().__init__()
        #self.reset(  context, eSleep=eSleep)

    def shouldProfileMemory(self) -> bool:
        return pmc_gcManager.PROFILE_MEMORY

    @classmethod
    def makeEntry(cls,   context:UpdateContext, eSleep:TimeSpanInSeconds=0.0) -> Self:
        """ NASTY!!! 
            the only reason this is overridden is to eliminate the cost of the 
            temporaries for *args and **kwds in CircuitPython GC
        """
        rp = cls.getReleasablePool()
        entry = cls._make_getFree( rp )

        if entry is None: entry = cls() # type: ignore
        entry.reset( context, eSleep=eSleep ) # pylint: disable=no-member # type: ignore
        
        return cls._makeFinish( rp, entry )

    def reset(self, context:UpdateContext,  eSleep:TimeSpanInSeconds=0.0):
        # nowPT = time.monotonic_ns()

        #self.currentUpdateIndex = 
        self.updateIndex = context.updateIndex
        self.eSleep = eSleep
        super().reset(context)


    def writeOn(self,config:ProfileWriteConfig,indent:str=''):
        return ProfilerRL.ProfileFrame_writeOn(self,config,indent)
    

class ProfileStubFrameEntry(ProfileSnapEntry): 
    def __init__(self,frame:Optional[ProfileFrameBase]=None):
        super().__init__()
            #tag="stub",when=TimeInSeconds(0))
        self.__frame = frame
        
    def subFrame(self, context, name:Optional[str]=None, name2:Optional[str]=None) -> 'ProfileFrameBase': # type: ignore
        return self.__frame  # type: ignore

    def writeOn(self,config:ProfileWriteConfig,indent:str=''):
        pass
    
    def jsonData(self,**kwds:StrAnyDict) -> Any:
        #rv = collections.OrderedDict(lw=self.lw, e=self.e, id=id(self), **self.etc)
        #return rv    
        return None
    
class ProfileStubFrame(ProfileFrame): 

    def __init__(self):
        super().__init__()
        self.when = 0
        self.updateIndex = -1
        self.__stubEntry = ProfileStubFrameEntry(self)
        
    def activeFrame(self) -> "ProfileFrameBase":
        return self

    def subFrame(self, context:UpdateContext, name:Optional[str]=None, name2:Optional[str]=None) -> 'ProfileSubFrame':
        return self # type: ignore

    def snap(self, name:str, name2:str|None = None, cls:type=ProfileSnapEntry ) -> ProfileSnapEntry:
        return self.__stubEntry
        
    
    def reset(self, context:UpdateContext,  eSleep:TimeSpanInSeconds=0.0):
        pass
        
    def __enter__(self):
        return self

    def __exit__(self,exc_type:Optional[Type[BaseException]], exc_value:Optional[BaseException], exc_tb:Optional[TracebackType]):
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
    
    def __init__(self, context:UpdateContext, timings:Optional[int]=None, stub:Optional[bool]=None ):
        if stub is None:
            stub = not pmc_mainLoopControl.ENABLE_PROFILE
            
        self.stubFrame = ProfileStubFrame()
        self._preContextIndex = context.updateIndex
        #if stub:
        #    self.timings = [ self.stubFrame ]
        #    timings = 1
        #else:
        timings = timings or pmc_mainLoopControl.profileTimings
        self.timings = [ ProfileFrame.makeEntry(context,0) for  _ in range(timings) ]
        
        self.timingsLength = timings
        self.disabled = stub
            
             
        #self.nextNewFrame(0)

    def nextNewFrame(self, context:UpdateContext, eSleep:TimeInSeconds=TimeInSeconds(0) ) -> ProfileFrame:
        updateIndex = context.updateIndex
        timingIndex = updateIndex % self.timingsLength 
        old = self.timings[timingIndex]
        if old is not None: # type:ignore[reportAttributeAccessIssue]
            old.release()
        self.currentTiming = ProfileFrame.makeEntry( context, eSleep=eSleep )
        self.timings[timingIndex] = self.currentTiming
        #self.currentTiming.reset( updateIndex, **kwds )
        return self.currentTiming
        
        #print( f"reset {updateIndex} {timingIndex} {self.currentTiming.updateIndex} {id(self.currentTiming)} ")
    
    def timingForUpdate( self, updateIndex:int ) -> ProfileFrame | None:
        if self.disabled: self.stubFrame

        timingIndex = updateIndex % self.timingsLength
        rv = self.timings[timingIndex]
        if rv is not None and rv.updateIndex != updateIndex: # type:ignore[reportAttributeAccessIssue]
            if rv.updateIndex != self._preContextIndex:
                print(f"tfy mismatch for {updateIndex} : [{timingIndex}].updateIndex={rv.updateIndex} {id(rv)}")
            return None
        return rv 

_sayProfilerImport.complete()
