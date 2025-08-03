from __future__ import annotations

import gc # type: ignore[reportUnusedImport]
import time, sys # type: ignore[reportUnusedImport]
import supervisor # type: ignore[reportUnusedImport]

from LumensalisCP.util.CountedInstance import CountedInstance

class mutableObject(CountedInstance):
    def __init__(self,**kwds:StrAnyDict) -> None:
        super().__init__()
        for tag,val in kwds.items():
            setattr(self, tag, val)

from LumensalisCP.CPTyping import *
