from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
import LumensalisCP.Main.Expressions
import LumensalisCP.Main.Manager
from LumensalisCP.Main.Dependents import MainRef

class UpdateContext(object):
    def __init__( self, main:"LumensalisCP.Main.Manager.MainManager"=None ):
        self.__updateIndex = 0
        self.__changedSources : List["LumensalisCP.Main.Expressions.InputSource"] = []
        self.__mainRef = MainRef( main )
        
    def reset( self ):
        self.__updateIndex += 1
        self.__changedSources = []

    @property
    def main(self) -> "LumensalisCP.Main.Manager.MainManager": return self.__mainRef()
        
    @property
    def when(self) -> TimeInSeconds : return self.main.when
    
    @property
    def updateIndex(self): return self.__updateIndex

    @property
    def changedSources(self): return self.__changedSources

    def addChangedSource( self, changed:"LumensalisCP.Main.Expressions.InputSource"):
        self.__changedSources.append( changed )



#############################################################################