
import board, microcontroller
from LumensalisCP.Main.Terms import *
from LumensalisCP.IOContext import  InputSource, NamedOutputTarget, EvaluationContext
from LumensalisCP.Scenes.Scene import addSceneTask
from LumensalisCP.Triggers import Trigger, fireOnSet, fireOnTrue, fireOnRising
from LumensalisCP.Temporal import Oscillator
from LumensalisCP.Demo.DemoBase import DemoBase, DemoSubBase, demoMain
from LumensalisCP.Lights.Patterns import *
from LumensalisCP.Lights.TestPatterns import *
from LumensalisCP.Temporal import Moving
from LumensalisCP.Behaviors import Motion, Behavior
from LumensalisCP.Main.Manager import MainManager
from TerrainTronics.Caernarfon.Castle import onIRCode
