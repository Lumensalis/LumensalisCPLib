
import LumensalisCP.Main.Updates
import time, math, asyncio, traceback, os, gc, wifi, displayio
import busio, board
import collections

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
from LumensalisCP.util.kwCallback import KWCallback
from LumensalisCP.util.bags import Bag

import LumensalisCP.Main.Profiler

def ProfileFrameEntry_writeOn(self:LumensalisCP.Main.Profiler.ProfileFrameEntry,target,indent='',minE=None,minF=None,**kwds):
    if self.e < minE and self.tag not in ['start', 'end']: return 
    target.write( f"{self.e:0.3f}{indent} {self.lw:0.3f} {self.tag:32s} @{id(self):X}\r\n" )
    #target.flush()
    if self.nest is not None:
        self.nest.writeOn( target, indent=indent+'# ',  minE=minE, minF=minF,**kwds)
    pass

def ProfileFrameBase_writeOn(self:LumensalisCP.Main.Profiler.ProfileFrameBase,target,indent='',minE=None,minF=None,**kwds):
    if self.e < minE: return
    target.write( f"{self.e:0.3f}{indent} {self._name:.22s} @{id(self):X} {self.start:0.3f} \r\n" )
    indent = indent+" ^ "
    for snap in self.entries:
        snap.writeOn(target,indent=indent, minE=minE, minF=minF, **kwds )

def ProfileFrame_writeOn(self:LumensalisCP.Main.Profiler.ProfileFrame,target,indent='',minE=None,minF=None,**kwds):
    minE = minE  if minE is not None else -1
    minF = minF or minE    
    if self.eSleep < min(minE,minF) and self.e < minF: return
    target.write( f"{self.e:0.3f}{indent} {self.start:0.3f} [{self.index}]@{id(self):X}\r\n" )
    indent = indent+"  "
    for snap in self.entries:
        snap.writeOn(target,indent=indent, minE=minE, minF=minF, **kwds )
