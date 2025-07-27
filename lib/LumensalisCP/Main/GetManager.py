

from __future__ import annotations

from LumensalisCP.Main.PreMainConfig import ImportProfiler
_sayMainGetManagerImport = ImportProfiler( "Main.GetManager" )

from LumensalisCP.CPTyping import TYPE_CHECKING

from LumensalisCP.util.Singleton import Singleton

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    
getMainManager:Singleton[MainManager] = Singleton("MainManager") # type: ignore

_sayMainGetManagerImport.complete()
