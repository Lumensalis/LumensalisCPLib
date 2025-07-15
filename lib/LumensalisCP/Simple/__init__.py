""" common imports for simple (typically single file, no class) projects

Intended to be used as `from LumensalisCP.Simple import *`
"""

from TerrainTronics.Demos.DemoCommon import *
from LumensalisCP.Lights.Values import RGB
from LumensalisCP.Main.Manager import MainManager

def ProjectManager( ) -> MainManager:
    return  MainManager.initOrGetManager()

def getColor( v ) -> RGB:
    return LightValueRGB.toRGB(v)