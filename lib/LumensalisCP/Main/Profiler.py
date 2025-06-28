
import LumensalisCP.Main.Updates
import time, math, asyncio, traceback, os, gc, wifi, displayio
import busio, board
import collections

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
from LumensalisCP.util.kwCallback import KWCallback
from LumensalisCP.util.bags import Bag

class ProfileFrameEntry(object): 
    tag:str
    lw: TimeSpanInSeconds
    e: TimeSpanInSeconds
    _nest:  "ProfileSubFrame"|None
    etc: Dict
    
    def __init__(self,tag:str, scd:"Profiler",**kwds):
        #super().__init__(*args,tag=tag,lw=scd.when, **kwds)
        self.tag = tag
        self.lw = scd.when
        self.e = 0.0
        self.etc = kwds

    @property 
    def nest( self ) -> "ProfileSubFrame"|None: return getattr(self,'_nest',None)
    
    #@nest.setter
    #def nest(self,v):
    #    self._nest = v
    
    def subFrame(self, context, name:str|None=None) -> 'ProfileSubFrame':
        assert self.nest is None
        self._nest = ProfileSubFrame(context,name)
        return self._nest
    
    def jsonData(self,**kwds):
        rv = collections.OrderedDict(lw=self.lw, e=self.e,  **self.etc)
        subFrame = self.nest
        if subFrame is not None:
            rv['nest'] = subFrame.jsonData() # **kwds)
        return rv


class ProfileFrameBase(object): 
    entries:List[ProfileFrameEntry]
    e:TimeSpanInSeconds
    when : TimeSpanInSeconds
    loopStartNS : int
    priorStartNS: int
    latestStartNS: int
    currentSnap: ProfileFrameEntry
    index: int
    depth: int = 0
    
    nextFrameIndex = 1

    def __init__(self):
        #super().__init__(*args, **kwds)
        self.entries = []
        self._name = '--'
        self.reset()
        
        
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
    
    def subFrame(self, context, name:str|None=None) -> 'ProfileSubFrame':
        if name is not None:
            snap = self.activeFrame().snap(name)
            return snap.subFrame(context,name)
        return self.activeEntry().subFrame(context,name)
    
    def reset(self ):
        nowNS = time.monotonic_ns()
        self.index = ProfileFrameBase.nextFrameIndex
        ProfileFrameBase.nextFrameIndex += 1
        
        self.entries.clear()
        self.e = 0
        self.start = 0
        self.when = 0
        self.latestStartNS = self.priorStartNS = self.loopStartNS = nowNS
        self.currentSnap = None

    def add( self, entry:ProfileFrameEntry):
        if( len(self.entries) ):
            self.e = entry.lw
        self.entries.append(entry)

    def snap(self, tag, **kwds ) -> ProfileFrameEntry:
        self.priorStartNS = self.latestStartNS
        self.latestStartNS = time.monotonic_ns()
        self.when = ( self.latestStartNS - self.loopStartNS ) * 0.000000001
        priorEntry = self.currentSnap
        entry =  ProfileFrameEntry( tag, self, **kwds )
        self.currentSnap = entry
        if priorEntry is not None:
            priorEntry.e = entry.lw - priorEntry.lw
        
        self.add( entry )
        return entry
        
    def jsonData(self,minF=None, minE = None, **kwds):
        minE = minE  if minE is not None else -1
        minF = minF or minE
        if self.e < minF: return None
        
        skipped = []
        rvEntries=collections.OrderedDict()
        for snap in self.entries:
            if snap.e < minE: 
                skipped.append(snap.tag)
                continue
            rvEntries[snap.tag] =  snap.jsonData(**kwds)
            #rvEntries.append( [snap.tag, snap.jsonData(**kwds)] )
            
        return dict(
            e= self.e,
            entries=rvEntries,
            skipped=skipped,
            i=self.index
        )
    
    def __str__(self):
        return f"PSF{('-'+self._name) if self._name is not None else ''}[{self.depth}:{self.index}]@{id(self):X}"
    
class ProfileSubFrame(ProfileFrameBase): 
    pass
    __context : 'LumensalisCP.Main.Updates.UpdateContext'
    
    def __init__(self, context:'LumensalisCP.Main.Updates.UpdateContext', name:str|None=None):
        super().__init__()
        self.__context = context
        self._name = name
        

        
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
            self.snap('end')
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


    def __init__(self):
        super().__init__()

    def reset(self, updateIndex =0):
        nowNS = time.monotonic_ns()

        self.updateIndex = updateIndex
        self.currentUpdateIndex = updateIndex
        super().reset()

    def jsonData(self,minF=None, minE = None, **kwds):
        baseData =super().jsonData(minF=minF, minE = minE, **kwds )
        if baseData is None: 
            return None
        return dict( i=self.updateIndex, **baseData )

class Profiler(object):
    currentUpdateIndex: int
    when: TimeInSeconds
    currentSnap: ProfileFrameEntry | None
    timingsLength:int 
    timings: List[ProfileFrame]
    currentTiming: ProfileFrame
    
    def __init__(self, timings=100):
        self.timingsLength = timings
        self.timings = [ProfileFrame() for _ in range(timings) ]
        #print( f"timings {id(self.timings[0])} through {id(self.timings[-1])}")
        
        self.reset(0)
        
    def reset(self, updateIndex) -> ProfileFrame: 
        timingIndex = updateIndex % self.timingsLength 
        self.currentTiming = self.timings[timingIndex]
        self.currentTiming.reset( updateIndex )
        return self.currentTiming
        
        #print( f"reset {updateIndex} {timingIndex} {self.currentTiming.updateIndex} {id(self.currentTiming)} ")
    
    def timingForUpdate( self, updateIndex ) -> ProfileFrame | None:
        timingIndex = updateIndex % self.timingsLength
        rv = self.timings[timingIndex]
        if rv.updateIndex != updateIndex:
            print(f"tfy mismatch for {updateIndex} : [{timingIndex}].updateIndex={rv.updateIndex} {id(rv)}")
            return None
        return rv 
        

