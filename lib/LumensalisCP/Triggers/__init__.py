from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( globals() ) # "Triggers.__init__"

_sayImport.complete(globals())


