""" common imports for simple (typically single file, no class) projects

Intended to be used as 
```python
from LumensalisCP.Simple import *
main = ProjectManager() 

# configure your project here...

main.launchProject( globals() )
```
more at http://lumensalis.com/ql/h2Start
"""
from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler
_saySimpleImport = getImportProfiler( __name__, globals() )

import rainbowio
import gc

# pyright: ignore[reportUnusedImport]
# pylint: disable=unused-import,import-error,unused-argument 
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

from LumensalisCP.Main.PreMainConfig import pmc_gcManager, pmc_mainLoopControl
pmc_mainLoopControl.sayAtStartup( "beginning import of LumensalisCP.Simple.__init__" )

from LumensalisCP.Main.PreMainConfig import *
from LumensalisCP.Lights.RGB import *
from LumensalisCP.Triggers.Action import do
from LumensalisCP.Demo.DemoCommon import *
from LumensalisCP.Main.Helpers import *
from LumensalisCP.Main.ProjectManager import ProjectManager

_saySimpleImport.parsing()

#############################################################################

_saySimpleImport.complete(globals())

pmc_mainLoopControl.sayAtStartup( "ending import of LumensalisCP.Simple.__init__ " )
