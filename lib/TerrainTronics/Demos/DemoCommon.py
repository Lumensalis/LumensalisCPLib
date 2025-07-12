from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Main.Terms import *
from LumensalisCP.IOContext import  InputSource, NamedOutputTarget, EvaluationContext
from LumensalisCP.Scenes.Scene import addSceneTask
from TerrainTronics.Caernarfon.Castle import onIRCode
from LumensalisCP.Triggers import Trigger, fireOnSet, fireOnTrue, fireOnRising
from .DemoBase import DemoBase, DemoSubBase
import board, microcontroller
from LumensalisCP.Lights.Patterns import *
from LumensalisCP.Lights.TestPatterns import *

from LumensalisCP.Behaviors import Motion
from LumensalisCP.Behaviors import Behavior