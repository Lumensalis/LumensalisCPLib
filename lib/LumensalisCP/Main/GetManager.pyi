

from LumensalisCP.util.Singleton import Singleton

from LumensalisCP.Main.Manager import MainManager


getMainManager = Singleton[MainManager] ("MainManager")
