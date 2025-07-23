

from __future__ import annotations
from LumensalisCP.CPTyping import TYPE_CHECKING

from LumensalisCP.util.Singleton import Singleton

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    
getMainManager:Singleton[MainManager] = Singleton("MainManager") # type: ignore

