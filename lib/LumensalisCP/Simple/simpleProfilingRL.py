

from LumensalisCP.Main.PreMainConfig import ReloadableImportProfiler
__saySimpleProfilingRLImport = ReloadableImportProfiler( "Simple.simpleProfilingRL" )

#from LumensalisCP.Demo.DemoCommon import *
#from LumensalisCP.Main.PreMainConfig import pmc_gcManager
from LumensalisCP.Main.Profiler import *
import sys
from collections import OrderedDict

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    from LumensalisCP.Main.Profiler import ProfileSnapEntry, ProfileFrame, ProfileSubFrame, ProfileFrameBase, ProfileWriteConfig


printDumpInterval = 28
collectionCheckInterval = 3.51

dumpConfig = ProfileWriteConfig(target=sys.stdout,
        minE = 0.000,
        minF=0.005,
        minSubF = 0.005,
        minB = 4,
        minEB = 4,
    )


__saySimpleProfilingRLImport.complete()
