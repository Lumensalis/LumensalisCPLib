from __future__ import annotations
import time, math, asyncio, traceback, os,  collections
import gc # type: ignore

# pylint: disable=wrong-import-position, unused-import, import-error, unused-argument
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false
# pylint: disable=import-error,unused-import,unused-argument

from LumensalisCP.Main.PreMainConfig import pmc_getImportProfiler
_sayCmPMMImport = pmc_getImportProfiler( "commonPreMainManager" )

import LumensalisCP.Debug
import LumensalisCP.Main
import LumensalisCP.Main.Dependents
import LumensalisCP.Main.Updates

from LumensalisCP.common import *

from LumensalisCP.Identity.Local import NliContainerMixin, NliList,NamedLocalIdentifiable, NliInterface

from LumensalisCP.util.kwCallback import KWCallback, KWCallbackArg
from LumensalisCP.util.bags import Bag

_sayCmPMMImport( "ConfigurableBase" )
from LumensalisCP.Controllers.ConfigurableBase import ConfigurableBase
_sayCmPMMImport( "Identity" )
from LumensalisCP.Controllers.Identity import ControllerIdentity, ControllerNVM

_sayCmPMMImport( "Expressions" )
from LumensalisCP.Eval.Expressions import EvaluationContext, UpdateContext

from LumensalisCP.Debug import Debuggable 
from LumensalisCP.Outputs import OutputTarget, NamedOutputTarget
from LumensalisCP.Inputs import InputSource

_sayCmPMMImport( "Scenes.Manager" )
from LumensalisCP.Scenes.Manager import SceneManager, Scene

_sayCmPMMImport( "Triggers.Timer" )
from LumensalisCP.Triggers.Timer import PeriodicTimerManager

_sayCmPMMImport( "Profiler" )
from LumensalisCP.Main.Profiler import Profiler, ProfileFrameBase, ProfileSnapEntry
_sayCmPMMImport( "Panel" )
from LumensalisCP.Main.Panel import PanelControl, PanelMonitor
_sayCmPMMImport( "Shutdown" )
from LumensalisCP.Main.Shutdown import ExitTask

_sayCmPMMImport( "I2CProvider" )
from LumensalisCP.Main.I2CProvider import I2CProvider

_sayCmPMMImport( "PreMainConfig" )
from LumensalisCP.Main import PreMainConfig
from LumensalisCP.Main.PreMainConfig import pmc_gcManager

pmc_mainLoopControl = PreMainConfig.pmc_mainLoopControl

_sayCmPMMImport.complete(globals())
