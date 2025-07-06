
import LumensalisCP.Main.Updates
import time, math, asyncio, traceback, os, gc, wifi, displayio
import busio, board
import collections

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
from LumensalisCP.util.kwCallback import KWCallback
from LumensalisCP.util.bags import Bag
from LumensalisCP.common import SHOW_EXCEPTION
import LumensalisCP.Main.Profiler

from LumensalisCP.Main._mconfig import gcm, _mlc

if getattr(  LumensalisCP.Main, 'Profiler', None ) is not None:
    LumensalisCP.Main.Profiler.ProfileFrameEntry.gcFixedOverhead = 112
    LumensalisCP.Main.Profiler.ProfileFrameBase.gcFixedOverhead = 0
    LumensalisCP.Main.Profiler.ProfileSubFrame.gcFixedOverhead = 0
    LumensalisCP.Main.Profiler.ProfileFrame.gcFixedOverhead = 0

def notEnoughMemUsed( self, config:"LumensalisCP.Main.Profiler.ProfileWriteConfig" ):
    return self.usedGC < config.minB if self.usedGC else not gcm.SHOW_ZERO_ALLOC_ENTRIES

def _heading( self ):
    if self.allocGc:
         #return f"   {self.e:0.3f} {self.usedGC:6d}/{self.rawUsedGC:6d}/{self.allocGc:7d}b"
         return f"   {self.e:0.3f} {self.usedGC:6d}b"
    else:
         return f"   {self.e:0.3f}"
         
         
def ProfileFrameEntry_writeOn(self:LumensalisCP.Main.Profiler.ProfileFrameEntry,config:"LumensalisCP.Main.Profiler.ProfileWriteConfig",indent=''):
    if self.e < config.minE and  notEnoughMemUsed(self, config): return # and self.tag not in ['start', 'end']: return 
    config.target.write( f"   {_heading(self)}{indent}:{self.lw:0.3f} {self.name:32s} {self.name2 or "":32s} @{id(self):X}\r\n" )

    if self.nest is not None:
        self.nest.writeOn( config, indent=indent+'# ')


def ProfileFrameBase_writeOn(self:LumensalisCP.Main.Profiler.ProfileFrameBase,config:"LumensalisCP.Main.Profiler.ProfileWriteConfig",indent=''):
    if self.e < config.minSubF and notEnoughMemUsed(self, config): return
    config.target.write( f"  {_heading(self)}{indent}>{self._name or "??":.22s} {self.name2 or "??":.22s}@{id(self):X} {self.start:0.3f} {getattr(self,'usedGC',0)}b\r\n" )
    indent = indent+" ^ "
    
    
    for x in range(self.entries):
        self.entry(x).writeOn(config,indent=indent)

def ProfileFrame_writeOn(self:LumensalisCP.Main.Profiler.ProfileFrame,config:"LumensalisCP.Main.Profiler.ProfileWriteConfig",indent=''):
    
    try:
        if self.eSleep < min(config.minE,config.minF) and self.e < config.minF and notEnoughMemUsed(self, config): 
            return
    except Exception as inst:
        if not _mlc.ENABLE_PROFILE:
            return 
        SHOW_EXCEPTION( inst, "ProfileFrame_writeOn check failed config=%r, eSleep=%r, e=%r, usedGC=%r", config, self.eSleep, self.e, self.usedGC )
        raise
    
    config.target.write( f"[{self._rIndex}] {_heading(self)}{indent} {self.start:0.3f} @{id(self):X}\r\n" )
    #return
    indent = indent+"  "
    for x in range(self.entries):
        assert type(x) is int
        entry = self.entry(x)
        if entry is None:
            config.writeLine( "  -- entry %r is None", x )
        else:
            ensure( isinstance( entry,  LumensalisCP.Main.Profiler.ProfileFrameEntry ), "entry (%r) is not ProfileFrameEntry", type(entry) )
            ensure( isinstance( config,  LumensalisCP.Main.Profiler.ProfileWriteConfig ) )
            ensure( type(indent) is str )
        
        #config.target.write( f" --- [{x}]\r\n");
        #ProfileFrameEntry_writeOn( entry, config, indent )
        entry.writeOn(config,indent=indent)
