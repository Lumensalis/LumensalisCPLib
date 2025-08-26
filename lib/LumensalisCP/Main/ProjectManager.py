
from __future__ import annotations

# pyright: ignore[reportUnusedImport]
# pylint: disable=unused-import,import-error,unused-argument 
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

from LumensalisCP.ImportProfiler import  getImportProfiler
import supervisor
_saySimpleImport = getImportProfiler( __name__, globals() )

import gc

from LumensalisCP.common import *
#from LumensalisCP.Triggers.Timer import PeriodicTimer
from LumensalisCP.Eval.EvaluationContext import EvaluationContext
from LumensalisCP.Temporal.Refreshable import *
from LumensalisCP.util.Reloadable import ReloadableModule, reloadableMethod, reloadableClassMeta
#from LumensalisCP.util.Reloadable import ReloadableMethodType, Unpack, KWDS

from LumensalisCP.Main.PreMainConfig import pmc_gcManager, pmc_mainLoopControl, sayAtStartup

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager

def ProjectManager( name:Optional[str]=None,
                        profile:Optional[bool]=None,
                    profileMemory:Optional[bool|int]=None,
                    useWifi:bool = True,
                    autoreload:Optional[bool] = True,
    ) -> MainManager:
    """ return the MainManager for a new simple project 
```python
from LumensalisCP.Simple import *
main = ProjectManager()

# configure your project here...

main.launchProject( globals() )
```
see http://lumensalis.com/ql/h2Main
"""
    if autoreload is not None:
        sayAtStartup( f"setting autoreload={autoreload}" )
        supervisor.runtime.autoreload = autoreload
        
    sayAtStartup( f"import MainManager" )
    from LumensalisCP.Main.Manager import MainManager
    if profile is not None:
        pmc_mainLoopControl.ENABLE_PROFILE = profile
        if profileMemory is not None:
            if isinstance(profileMemory, bool):
                pmc_gcManager.PROFILE_MEMORY = profileMemory
            else:
                pmc_gcManager.PROFILE_MEMORY = True
                if profileMemory & 1: pmc_gcManager.PROFILE_MEMORY_NESTED = True
                if profileMemory & 2: pmc_gcManager.PROFILE_MEMORY_ENTRIES = True

    if pmc_mainLoopControl.ENABLE_PROFILE:
        sayAtStartup( f"preloading profiler releasables" )
        from LumensalisCP.Main.Profiler import ProfileFrame,ProfileSnapEntry,ProfileSubFrame,ProfileFrameBase
        ProfileFrame.releasablePreload( 70 )
        ProfileSubFrame.releasablePreload( 1000 )
        ProfileSnapEntry.releasablePreload( 3000 )

    sayAtStartup( f"Project: get main" )
    main = MainManager.initManager(name=name)

    main.useWifi = useWifi

    #if pmc_gcManager.PROFILE_MEMORY == True:
    #    pmc_gcManager.PROFILE_MEMORY_NESTED = True
    #    pmc_gcManager.PROFILE_MEMORY_ENTRIES = True
    
    pmc_mainLoopControl.sayAtStartup(f"ProjectManager: starting project, profiling={pmc_mainLoopControl.ENABLE_PROFILE}, useWifi={main.useWifi}")
    
    gc.collect() # collect garbage before starting the project
    gc.disable()

    return main

_saySimpleImport.complete(globals())
