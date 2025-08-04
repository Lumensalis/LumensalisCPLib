
from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( __name__, globals() )

import atexit

from LumensalisCP.common import *

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager


class ExitTask(object):
    
    def __init__(self, main:MainManager, task:Callable[...,Any], name:Optional[str]=None ):
        self.name = name or task.__name__
        self.__main = main
        self.__task = task
        self.__called = False
        
        self.__registerable = self.__callIt
        atexit.register( self.__registerable)
    
    def shutdown(self):
        self.__callIt()
        
    def __callIt(self):
        if self.__called is True:
            print( f"EXITER {self.name} already called" )
            return
        try:
            self.__task()
        except:
            print( f"EXITER {self.name} FAILED" )
        self.__called = True

_sayImport.complete()