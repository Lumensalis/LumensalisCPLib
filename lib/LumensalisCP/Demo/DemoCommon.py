from __future__ import annotations

# pylint: disable=unused-import,import-error,unused-argument
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

import board, microcontroller

from LumensalisCP.Main.PreMainConfig import ImportProfiler
_sayDemoCommonImport = ImportProfiler( "DemoCommon" )


from LumensalisCP.common import *
from LumensalisCP.Eval.common import *
_sayDemoCommonImport( "addSceneTask" )
from LumensalisCP.Scenes.Scene import addSceneTask
_sayDemoCommonImport( "Trigger" )
from LumensalisCP.Triggers.common import Trigger
from LumensalisCP.Triggers.common import fireOnSet, fireOnTrue, fireOnRising, fireOnFalling
from LumensalisCP.Temporal import Oscillator
_sayDemoCommonImport( "DemoBase" )
from LumensalisCP.Demo.DemoBase import DemoBase, DemoSubBase, demoMain
_sayDemoCommonImport( "Patterns" )
from LumensalisCP.Lights.Patterns import *
_sayDemoCommonImport( "TestPatterns" )
from LumensalisCP.Lights.TestPatterns import *
_sayDemoCommonImport( "Temporal" )
from LumensalisCP.Temporal import Moving
_sayDemoCommonImport( "Motion" )
from LumensalisCP.Behaviors import Motion, Behavior
_sayDemoCommonImport( "MainManager" )
from LumensalisCP.Main.Manager import MainManager
_sayDemoCommonImport( "onIRCode" )
from TerrainTronics.Caernarfon.Castle import onIRCode

_sayDemoCommonImport.complete()
