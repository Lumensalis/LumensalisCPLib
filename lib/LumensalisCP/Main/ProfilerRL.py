from __future__ import annotations


import time, math, asyncio, traceback, os, collections
import gc # type: ignore
import wifi, displayio
import busio, board

import LumensalisCP.Main.Updates

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
from LumensalisCP.util.kwCallback import KWCallback, KWCallbackArg
from LumensalisCP.util.bags import Bag
from LumensalisCP.common import SHOW_EXCEPTION
import LumensalisCP.Main.Profiler

from LumensalisCP.Main.PreMainConfig import pmc_gcManager, pmc_mainLoopControl
# pylint: disable=unused-argument, redefined-outer-name, attribute-defined-outside-init,protected-access,bad-indentation

def _rl_setFixedOverheads():
    LumensalisCP.Main.Profiler.ProfileSnapEntry.gcFixedOverhead = 0
    LumensalisCP.Main.Profiler.ProfileFrameBase.gcFixedOverhead = 0
    LumensalisCP.Main.Profiler.ProfileSubFrame.gcFixedOverhead = 0
    LumensalisCP.Main.Profiler.ProfileFrame.gcFixedOverhead = 0

if getattr(  LumensalisCP.Main, 'Profiler', None ) is not None:
    _rl_setFixedOverheads()

def notEnoughMemUsed( self, config:"LumensalisCP.Main.Profiler.ProfileWriteConfig" ):
    return self.usedGC < config.minB if self.usedGC else not pmc_gcManager.SHOW_ZERO_ALLOC_ENTRIES

def _heading( self ):
    if self.allocGc:
         #return f"   {self.e:0.3f} {self.usedGC:6d}/{self.rawUsedGC:6d}/{self.allocGc:7d}b"
         return f"   {self.e:0.3f} {self.usedGC:6d}b"
    else:
         return f"   {self.e:0.3f}"
         
         
def ProfileFrameEntry_writeOn(self:LumensalisCP.Main.Profiler.ProfileSnapEntry,config:"LumensalisCP.Main.Profiler.ProfileWriteConfig",indent=''):
    if self.e < config.minE and  notEnoughMemUsed(self, config): return # and self.tag not in ['start', 'end']: return 
    config.target.write( f"   {_heading(self)}{indent}:{self.lw:0.3f} {self.name:32s} {self.name2 or '':32s} @{id(self):X}\r\n" )

    if self.nest is not None:
        self.nest.writeOn( config, indent=indent+'# ')


def ProfileFrameBase_iterSnaps(self:LumensalisCP.Main.Profiler.ProfileFrameBase):
    entry = self.firstSnap
    while entry is not None:
        yield entry
        entry = entry._nextSnap
    

def ProfileFrameBase_writeOn(self:LumensalisCP.Main.Profiler.ProfileFrameBase,config:"LumensalisCP.Main.Profiler.ProfileWriteConfig",indent=''):
    if self.e < config.minSubF and notEnoughMemUsed(self, config): return
    #config.target.write( f"   {_heading(self)}{indent}>{self._name or '??':.22s} {self.name2 or '??':.22s}@{id(self):X} {self.start:0.3f} {getattr(self,'usedGC',0)}b\r\n" )
    config.target.write( f"   {_heading(self)}{indent}>{self._name or '??':.22s}@{id(self):X} {self.start:0.3f} {getattr(self,'usedGC',0)}b\r\n" )
    indent = indent+" ^ "
    
    
    #for x in range(self.entries):
    #    self.entry(x).writeOn(config,indent=indent)
    for snap in self.iterSnaps():
        snap.writeOn(config,indent=indent)

def ProfileFrame_writeOn(self:LumensalisCP.Main.Profiler.ProfileFrame,config:"LumensalisCP.Main.Profiler.ProfileWriteConfig",indent=''):
    
    try:
        if self.eSleep < min(config.minE,config.minF) and self.e < config.minF and notEnoughMemUsed(self, config): 
            return
    except Exception as inst:
        if not pmc_mainLoopControl.ENABLE_PROFILE:
            return 
        SHOW_EXCEPTION( inst, "ProfileFrame_writeOn check failed config=%r, eSleep=%r, e=%r, usedGC=%r", config, self.eSleep, self.e, self.usedGC )
        raise
    
    config.target.write( f"[{self._rIndex}] {_heading(self)}{indent} {self.start:0.3f} @{id(self):X}\r\n" )
    #return
    indent = indent+"  "
    #for x in range(self.entries):
    #    assert type(x) is int
    #    entry = self.entry(x)
    #    if entry is None:
    #        config.writeLine( "  -- entry %r is None", x )
    #    else:
    for entry in self.iterSnaps():        
        ensure( isinstance( entry,  LumensalisCP.Main.Profiler.ProfileSnapEntry ), "entry (%r) is not ProfileSnapEntry", type(entry) )
        ensure( isinstance( config,  LumensalisCP.Main.Profiler.ProfileWriteConfig ) )
        ensure( isinstance(indent, str ) )
    
        #config.target.write( f" --- [{x}]\r\n");
        #ProfileFrameEntry_writeOn( entry, config, indent )
        entry.writeOn(config,indent=indent)
