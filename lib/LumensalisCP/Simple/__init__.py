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
if False:
    #import LumensalisCP.Simple
    import LumensalisCP.Identity.Local
    import LumensalisCP.Main.Updates
    import LumensalisCP.util.kwCallback
    import LumensalisCP.Eval.EvaluationContext 
    import LumensalisCP.Eval.ExpressionTerm 
    import LumensalisCP.Eval.Terms 
    import LumensalisCP.Eval.Evaluatable 
    import LumensalisCP.Eval.common
    import LumensalisCP.Inputs
    import LumensalisCP.Outputs
    import LumensalisCP.IOContext
    import LumensalisCP.Triggers 
#from LumensalisCP.Triggers.Timer import addPeriodicTaskDef, addSimplePeriodicTaskDef, PeriodicTimerManager, PeriodicTimer
#from LumensalisCP.Triggers.Action import *
#from LumensalisCP.Behaviors.Behavior import Behavior, Actor 
#from LumensalisCP.Behaviors.Behavior import Behavior as BehaviorClass
#from LumensalisCP.Main.Manager import MainManager
#from LumensalisCP.Audio.Effect import *
from LumensalisCP.Demo.DemoCommon import *
from LumensalisCP.Main.ProjectManager import ProjectManager

_saySimpleImport.parsing()

#############################################################################


_saySimpleImport.complete(globals())

pmc_mainLoopControl.sayAtStartup( "ending import of LumensalisCP.Simple.__init__ " )
