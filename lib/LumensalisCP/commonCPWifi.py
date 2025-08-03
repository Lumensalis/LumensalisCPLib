"""grouped import for common CircuitPython Wifi / http specific modules

Intended to be uses as `from LumensalisCP.commonCPWifi import *`

Partly for convenience and DRY, but also to minimize missing import problem reports
"""

# pylint: disable=unused-import,import-error,unused-argument
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false
# pyright: reportUnknownVariableType=false

from LumensalisCP.ImportProfiler import  getImportProfiler
__sayImport = getImportProfiler( __name__, globals() )


from LumensalisCP.commonCP import *
import adafruit_httpserver # type: ignore
import wifi,  mdns


__sayImport.complete()