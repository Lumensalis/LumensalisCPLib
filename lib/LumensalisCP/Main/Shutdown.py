
from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
import atexit

import LumensalisCP.Main.Manager

class ExitTask(object):
    
    def __init__(self, main:"LumensalisCP.Main.Manager.MainManager", task:Callable, name:str=None ):
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
