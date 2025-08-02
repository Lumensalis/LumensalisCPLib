
from __future__ import annotations

import rainbowio
import gc

# pyright: ignore[reportUnusedImport]
# pylint: disable=unused-import,import-error,unused-argument 
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false


from LumensalisCP.ImportProfiler import  getImportProfiler
_saySimpleImport = getImportProfiler( __name__, globals() )

from LumensalisCP.common import *
#from LumensalisCP.Triggers.Timer import PeriodicTimer
from LumensalisCP.Eval.EvaluationContext import EvaluationContext
from LumensalisCP.Temporal.Refreshable import *
from LumensalisCP.util.Reloadable import ReloadableModule, reloadableMethod, reloadableClassMeta
#from LumensalisCP.util.Reloadable import ReloadableMethodType, Unpack, KWDS

from LumensalisCP.Main.PreMainConfig import pmc_gcManager, pmc_mainLoopControl


if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager

def ProjectManager( profile:Optional[bool]=None,
                    profileMemory:Optional[bool|int]=None,
                    useWifi:bool = True,
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
        from LumensalisCP.Main.Profiler import ProfileFrame,ProfileSnapEntry,ProfileSubFrame,ProfileFrameBase
        ProfileFrame.releasablePreload( 70 )
        ProfileSubFrame.releasablePreload( 1000 )
        ProfileSnapEntry.releasablePreload( 3000 )

    main = MainManager.initOrGetManager()

    main.useWifi = useWifi

    #if pmc_gcManager.PROFILE_MEMORY == True:
    #    pmc_gcManager.PROFILE_MEMORY_NESTED = True
    #    pmc_gcManager.PROFILE_MEMORY_ENTRIES = True
    if  pmc_mainLoopControl.ENABLE_PROFILE:
        pmc_mainLoopControl.sayAtStartup("ProjectManager: starting project with profiling enabled")
    
    gc.collect() # collect garbage before starting the project
    gc.disable()

    def addProfilingCallbacks():
        print("\n\nAdding profiling callbacks...\n")
        import LumensalisCP.Main.ProfilerRL as profilingRL
        #profilingRL.printDump(rv)

        def getCollectionCheckInterval() -> TimeSpanInSeconds:
            rv = pmc_gcManager.collectionCheckInterval
            return rv
        
        #timer = PeriodicTimer(manager=main.timers,name="gc-collect",
         #                     interval=getCollectionCheckInterval, oneShot=False)
        
        #@addPeriodicTaskDef( name="gc-collect", interval=getCollectionCheckInterval, main=main )
        def runCollect(context:EvaluationContext) -> None:
            #print( f"pmc_gcManager.runCollection {context.updateIndex}..." )
            pmc_gcManager.runCollection(context, show=pmc_gcManager.showRunCollection)

        #timer.addAction(runCollect)
        #timer.start()
        print("\n\n profiling callbacks added...\n")
        #@addPeriodicTaskDef( "print-dump", period=lambda: profilingRL.printDumpInterval, main=main )
        #def dump():
        #    profilingRL.printDump(main)

    #main.callLater( addProfilingCallbacks )
    return main

_saySimpleImport.complete(globals())
