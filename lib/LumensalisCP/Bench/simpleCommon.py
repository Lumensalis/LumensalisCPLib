from __future__ import annotations

# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

import gc 
import time, sys 
import supervisor

from LumensalisCP.util.CountedInstance import CountedInstance
from LumensalisCP.pyCp import weakref
from LumensalisCP.Temporal.Time import TimeInSeconds, getOffsetNow


class mutableObject(CountedInstance):
    def __init__(self,**kwds:StrAnyDict) -> None:
        super().__init__()
        for tag,val in kwds.items():
            setattr(self, tag, val)

from LumensalisCP.CPTyping import *
