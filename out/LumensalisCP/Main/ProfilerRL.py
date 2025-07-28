from __future__ import annotations


import gc # type: ignore

from LumensalisCP.Main.PreMainConfig import ReloadableImportProfiler
__sayMainProfilerRLImport = ReloadableImportProfiler( "Main.ProfilerRL" )

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
from LumensalisCP.common import SHOW_EXCEPTION
import LumensalisCP.Main.Profiler

if TYPE_CHECKING:

    from LumensalisCP.Main.Profiler import ProfileSnapEntry, ProfileFrame, ProfileFrameBase, ProfileWriteConfig
    #from LumensalisCP.Main.Manager import MainManager   

from LumensalisCP.Main.PreMainConfig import pmc_gcManager, pmc_mainLoopControl
# pylint: disable=unused-argument, redefined-outer-name, attribute-defined-outside-init,protected-access,bad-indentation

def _rl_setFixedOverheads():
    LumensalisCP.Main.Profiler.ProfileSnapEntry.gcFixedOverhead = 0
    LumensalisCP.Main.Profiler.ProfileFrameBase.gcFixedOverhead = 0
    LumensalisCP.Main.Profiler.ProfileSubFrame.gcFixedOverhead = 0
    LumensalisCP.Main.Profiler.ProfileFrame.gcFixedOverhead = 0

if getattr(  LumensalisCP.Main, 'Profiler', None ) is not None:
    _rl_setFixedOverheads()

def notEnoughMemUsed( self:ProfileSnapEntry|ProfileFrameBase, config:ProfileWriteConfig ) -> bool:
    return self.usedGC < config.minB if self.usedGC else not pmc_gcManager.SHOW_ZERO_ALLOC_ENTRIES

def _heading( self:ProfileFrameBase|ProfileSnapEntry ) -> str:
    if self.allocGc:
         #return f"   {self.e:0.3f} {self.usedGC:6d}/{self.rawUsedGC:6d}/{self.allocGc:7d}b"
         return f"   {self.e:0.3f} {self.usedGC:6d}b"
    else:
         return f"   {self.e:0.3f}"

def ProfileFrameEntry_writeOn(self:ProfileSnapEntry,config:ProfileWriteConfig,indent:str='') -> None:
    if self.e < config.minE and  notEnoughMemUsed(self, config): return # and self.tag not in ['start', 'end']: return 

    if config.makingJson:
        data = config.top
        assert isinstance(data, dict), f"Invalid data type {type(data)} for ProfileWriteConfig"
        data['name'] = self.name
        if self.name2 is not None:
            data['name2'] = self.name2
        data['lw'] = self.lw
        data['e'] = self.e
        if self.allocGc:
             data['usedGC'] = self.usedGC

        if self.nest is not None:
            with config.nestDict( 'nest'):
                self.nest.writeOn( config )
    
    else:
        config.writeLine( f"   {_heading(self)}{indent}:{self.lw:0.3f} {self.name:32s} {self.name2 or '':32s} @{id(self):X}" )

        if self.nest is not None:
            self.nest.writeOn( config, indent=indent+'# ')

def ProfileFrameBase_iterSnaps(self:ProfileFrameBase):
    entry = self.firstSnap
    while entry is not None:
        yield entry
        entry = entry._nextSnap # type:ignore[reportAttributeAccessIssue]

def ProfileFrameBase_writeOn(self:ProfileFrameBase,config:ProfileWriteConfig,indent:str=''):
    if self.e < config.minSubF and notEnoughMemUsed(self, config): return

    if config.makingJson:
        data = config.topDict
        data['name'] = self.name
        data['e'] = self.e
        usedGC = self.usedGC
        if usedGC: data['usedGC'] = usedGC
        data['start'] = self.start

        with config.nestList( 'snaps' ):
            for snap in self.iterSnaps():
                with config.nestDict(  ):
                    snap.writeOn(config)

    else:
        #config.target.write( f"   {_heading(self)}{indent}>{self._name or '??':.22s} {self.name2 or '??':.22s}@{id(self):X} {self.start:0.3f} {getattr(self,'usedGC',0)}b\r\n" )
        config.writeLine( f"   {_heading(self)}{indent}>{self.name or '??':.22s}@{id(self):X} {self.start:0.3f} {getattr(self,'usedGC',0)}b" )
        indent = indent+" ^ "
        
        
        #for x in range(self.entries):
        #    self.entry(x).writeOn(config,indent=indent)
        for snap in self.iterSnaps():
            snap.writeOn(config,indent=indent)

def ProfileFrame_writeOn(self:ProfileFrame,config:ProfileWriteConfig,indent:str=''):
    
    try:
        if self.eSleep < min(config.minE,config.minF) and self.e < config.minF and notEnoughMemUsed(self, config): 
            return
    except Exception as inst:
        if not pmc_mainLoopControl.ENABLE_PROFILE:
            return 
        SHOW_EXCEPTION( inst, "ProfileFrame_writeOn check failed config=%r, eSleep=%r, e=%r, usedGC=%r", config, self.eSleep, self.e, self.usedGC )
        raise

    if config.makingJson:
        data = config.topDict
        data['rindex'] = self.rindex
        data['e'] = self.e
        usedGC = self.usedGC
        if usedGC: data['usedGC'] = usedGC
        data['start'] = self.start
        data['eSleep'] = self.eSleep

        with config.nestList( 'snaps' ):
            for snap in self.iterSnaps():
                with config.nestDict(  ):
                    snap.writeOn(config)
    else:
        config.writeLine( f"[{self.rindex}] {_heading(self)}{indent} {self.start:0.3f} @{id(self):X}" )
        #return
        indent = indent+"  "
        #for x in range(self.entries):
        #    assert type(x) is int
        #    entry = self.entry(x)
        #    if entry is None:
        #        config.writeLine( "  -- entry %r is None", x )
        #    else:
        for entry in self.iterSnaps():        
            #assert isinstance( entry,  ProfileSnapEntry ), f"entry {type(entry) } is not ProfileSnapEntry"
            #assert isinstance( config,  ProfileWriteConfig ) 
            assert isinstance(indent, str ) 
        
            #config.target.write( f" --- [{x}]\r\n");
            #ProfileFrameEntry_writeOn( entry, config, indent )
            entry.writeOn(config,indent=indent)

__sayMainProfilerRLImport.complete()
