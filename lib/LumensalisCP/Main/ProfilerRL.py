from __future__ import annotations

# pyright: reportUnusedImport=false, reportUnusedVariable=false

import gc # type: ignore
import sys
from collections import OrderedDict

from LumensalisCP.ImportProfiler import getImportProfiler, getReloadableImportProfiler
__sayMainProfilerRLImport = getImportProfiler( globals(), reloadable=True  )

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
from LumensalisCP.common import SHOW_EXCEPTION
import LumensalisCP.Main.Profiler
from LumensalisCP.util.Reloadable import reloadableClassMeta, ReloadableModule
if TYPE_CHECKING:

    from LumensalisCP.Main.Manager import MainManager
    from LumensalisCP.Main.Profiler import ProfileSnapEntry, ProfileFrame, ProfileSubFrame, ProfileFrameBase, ProfileWriteConfig

    #from LumensalisCP.Main.Profiler import ProfileSnapEntry, ProfileFrame, ProfileFrameBase, ProfileWriteConfig
    #from LumensalisCP.Main.Manager import MainManager   

from LumensalisCP.Main.PreMainConfig import pmc_gcManager, pmc_mainLoopControl
# pylint: disable=unused-argument, redefined-outer-name, attribute-defined-outside-init,protected-access,bad-indentation


def _rl_setFixedOverheads():
    LumensalisCP.Main.Profiler.ProfileSnapEntry.gcFixedOverhead = 0
    LumensalisCP.Main.Profiler.ProfileFrameBase.gcFixedOverhead = 0
    LumensalisCP.Main.Profiler.ProfileSubFrame.gcFixedOverhead = 0
    LumensalisCP.Main.Profiler.ProfileFrame.gcFixedOverhead = 0


if getattr(  LumensalisCP.Main, 'Profiler', None ) is not None:
    from LumensalisCP.Main.Profiler import ProfileSnapEntry, ProfileFrame, ProfileSubFrame, ProfileFrameBase, ProfileWriteConfig
    _rl_setFixedOverheads()

def _heading( self:ProfileFrameBase|ProfileSnapEntry ) -> str:
    if self.allocGc:
         #return f"   {self.e:0.3f} {self.usedGC:6d}/{self.rawUsedGC:6d}/{self.allocGc:7d}b"
         return f"   {self.e:0.3f} {self.usedGC:6d}b"
    else:
         return f"   {self.e:0.3f}"

# pyright: reportRedeclaration=false
_module = ReloadableModule( 'LumensalisCP.Main.Profiler' )
_ProfileSnapEntry = _module.reloadableClassMeta('ProfileSnapEntry' )
_ProfileFrameBase = _module.reloadableClassMeta('ProfileFrameBase' )
_ProfileFrame = _module.reloadableClassMeta('ProfileFrame' )
_ProfileSubFrame = _module.reloadableClassMeta('ProfileSubFrame' )

@_ProfileSnapEntry.reloadableMethod()
def writeOn(self:ProfileSnapEntry,config:ProfileWriteConfig,indent:str='') -> None:
    if not  config.shouldShowSnap(self): return

    if config.makingJson:
        data = config.top
        assert isinstance(data, dict), f"Invalid data type {type(data)} for ProfileWriteConfig"
        data['name'] = self.name
        if self.name2 is not None:
            data['name2'] = self.name2
        data['lw'] = self.lw
        data['e'] = self.e
        if config.showMemoryEntries:
            if self.allocGc:
                data['usedGC'] = self.usedGC
                data['rawUsedGC'] = self.rawUsedGC
                data['allocGc'] = self.allocGc

        if self.nest is not None:
            with config.nestDict( 'nest'):
                self.nest.writeOn( config )
    
    else:
        config.writeLine( f"   {_heading(self)}{indent}:{self.lw:0.3f} {self.name:32s} {self.name2 or '':32s} @{id(self):X}" )

        if self.nest is not None:
            self.nest.writeOn( config, indent=indent+'# ')

@_ProfileFrameBase.reloadableMethod()
def iterSnaps(self:ProfileFrameBase):
    entry = self.firstSnap
    while entry is not None:
        yield entry
        entry = entry._nextSnap # type:ignore[reportAttributeAccessIssue]

@_ProfileFrameBase.reloadableMethod()
def writeOn(self:ProfileFrameBase,config:ProfileWriteConfig,indent:str=''):
    if not config.shouldShowFrame(self):
        return
    
    if config.makingJson:
        data = config.topDict
        data['name'] = self.name
        data['e'] = self.e
        if config.showMemory:
            usedGC = self.usedGC
            if usedGC: data['usedGC'] = usedGC
            data['rawUsedGC'] = self.rawUsedGC
            data['allocGc'] = self.allocGc

        data['start'] = self.start

        with config.nestList( 'snaps' ):
            for snap in self.iterSnaps():
                with config.nestDict(  ):
                    snap.writeOn(config)

    else:
        #config.target.write( f"   {_heading(self)}{indent}>{self._name or '??':.22s} {self.name2 or '??':.22s}@{id(self):X} {self.start:0.3f} {getattr(self,'usedGC',0)}b\r\n" )
        config.writeLine( f"   {_heading(self)}{indent}>{self.name or '??':.22s}@{id(self):X} {self.start:0.3f} {getattr(self,'usedGC',0)}b" )
        indent = indent+" ^ "

        for snap in self.iterSnaps():
            snap.writeOn(config,indent=indent)

@_ProfileFrame.reloadableMethod()
def writeOn(self:ProfileFrame,config:ProfileWriteConfig,indent:str=''):
    if not config.shouldShowFrame(self): return

    if config.makingJson:
        data = config.topDict
        data['rindex'] = self.rindex
        data['e'] = self.e
        if config.showMemory:
            usedGC = self.usedGC
            if usedGC: data['usedGC'] = usedGC
        data['start'] = self.start
        data['eSleep'] = self.eSleep

        with config.nestList( 'snaps' ):
            for snap in self.iterSnaps():
                if config.shouldShowSnap(snap):
                    with config.nestDict( ):
                        snap.writeOn(config)
    else:
        config.writeLine( f"[{self.rindex}] {_heading(self)}{indent} {self.start:0.3f} @{id(self):X}" )
        #return
        indent = indent+"  "

        for entry in self.iterSnaps():        
            #assert isinstance( entry,  ProfileSnapEntry ), f"entry {type(entry) } is not ProfileSnapEntry"
            #assert isinstance( config,  ProfileWriteConfig ) 
            assert isinstance(indent, str ) 
        
            #config.target.write( f" --- [{x}]\r\n");
            #ProfileSnapEntry_writeOn( entry, config, indent )
            entry.writeOn(config,indent=indent)


#############################################################################

def addPoolInfo( dest:StrAnyDict,  cls:type[ProfileSnapEntry|ProfileFrame|ProfileSubFrame|ProfileFrameBase]) -> Any:
    pool = cls.getReleasablePool()
    return dictAddUnique(dest, cls.__name__, dict( a=pool._allocs, r=pool._releases ) ) # type: ignore

def getProfilerInfo( main:MainManager, dumpConfig:Optional[ProfileWriteConfig]=None ) -> Any:

    context = main.getContext()
    i = context.updateIndex
    print(f"getProfilerInfo: updateIndex = {i}")
    
    if dumpConfig is None:

        rv:StrAnyDict = OrderedDict()
        dumpConfig = ProfileWriteConfig(target=rv,
                minE = 0.005,
                minF=0.01,
                minSubF = 0.05,
                minB = 0,
                minEB = 0,
            )
    else:
        rv = dumpConfig.target
    
    if not isinstance(rv, (dict,OrderedDict)  ): # pyright: ignore[reportUnnecessaryIsInstance]
        raise TypeError(f"dumpConfig.target is not a dict: {type(rv)}")

    with dumpConfig.nestDict('dumpConfig'):
        d = dumpConfig.topDict
        d['minE'] = dumpConfig.minE
        d['minEB'] = dumpConfig.minEB
        d['minF'] = dumpConfig.minF
        d['minSubF'] = dumpConfig.minSubF
        d['minB'] = dumpConfig.minB


    with dumpConfig.nestDict('pools'):
        d = dumpConfig.topDict
        addPoolInfo( d, ProfileSnapEntry )
        addPoolInfo( d, ProfileFrame )
        addPoolInfo( d, ProfileSubFrame )
        addPoolInfo( d, ProfileFrameBase )

    with dumpConfig.nestDict('gc'):
        d = dumpConfig.topDict
        d['mem_alloc'] = gc.mem_alloc()
        d['mem_free'] = gc.mem_free()

    with dumpConfig.nestDict('timers'):
        d = dumpConfig.topDict
        d['timerSorts'] = main.timers.timerSorts
        d['timerChanges'] = [ dict(
            name=timer.name,
            running=timer.running,
            nextFire=timer.nextFire,    
            lastFire=timer.lastFire,
            
        )
            for timer in main.timers.timers]
        
    count = 10
    
    with dumpConfig.nestList('frames'):
        
        while count and i >= 0:
            count -= 1
            frame = main.profiler.timingForUpdate( i )
            
            if frame is not None:
                with dumpConfig.nestDict():
                    frame.writeOn( dumpConfig )
            i -= 1


    
    return rv


#############################################################################



__sayMainProfilerRLImport.complete(globals())
