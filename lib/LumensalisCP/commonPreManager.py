from __future__ import annotations


# pylint: disable=wrong-import-position, unused-import, import-error, unused-argument
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false
# pylint: disable=import-error,unused-import,unused-argument

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayCmPMMImport = getImportProfiler( __name__, globals())

import time, math, traceback, os,  collections
import gc # type: ignore

import LumensalisCP.Debug
import LumensalisCP.Main
import LumensalisCP.Main.Dependents
import LumensalisCP.Main.Updates

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import NliContainerMixin, NliList,NamedLocalIdentifiable, NliInterface
from LumensalisCP.util.bags import Bag
from LumensalisCP.Eval.Expressions import EvaluationContext, UpdateContext
from LumensalisCP.Debug import Debuggable, IDebuggable 
from LumensalisCP.Outputs import OutputTarget, NamedOutputTarget
from LumensalisCP.Inputs import InputSource
from LumensalisCP.Main.Profiler import Profiler, ProfileFrameBase, ProfileSnapEntry
from LumensalisCP.Main.Shutdown import ExitTask
from LumensalisCP.Main import PreMainConfig
from LumensalisCP.Main.PreMainConfig import pmc_gcManager

if TYPE_CHECKING:
    from LumensalisCP.Scenes.Manager import SceneManager, Scene
    from LumensalisCP.Triggers.Timer import PeriodicTimerManager
    from LumensalisCP.Main.Panel import PanelControl, PanelMonitor
    from LumensalisCP.Main.I2CProvider import I2CProvider
    from LumensalisCP.util.kwCallback import KWCallback, KWCallbackArg
    from LumensalisCP.Controllers.ConfigurableBase import ConfigurableBase
    from LumensalisCP.Controllers.Identity import ControllerIdentity, ControllerNVM


_sayCmPMMImport.parsing()

pmc_mainLoopControl = PreMainConfig.pmc_mainLoopControl

_sayCmPMMImport.complete(globals())
