
from LumensalisCP.Main.Terms import *
from LumensalisCP.IOContext import  InputSource, NamedOutputTarget, EvaluationContext, OptionalContextArg
from LumensalisCP.Scenes.Scene import addSceneTask
from TerrainTronics.Caernarfon.Castle import onIRCode
from LumensalisCP.Triggers import Trigger, fireOnSet, fireOnTrue, fireOnRising
from LumensalisCP.Temporal import Oscillator
from .DemoBase import DemoBase, DemoSubBase, demoMain
import board, microcontroller
from LumensalisCP.Lights.Patterns import *
from LumensalisCP.Lights.TestPatterns import *
from LumensalisCP.Temporal import Moving
from LumensalisCP.Behaviors import Motion
from LumensalisCP.Behaviors import Behavior
from LumensalisCP.Main.Manager import MainManager
