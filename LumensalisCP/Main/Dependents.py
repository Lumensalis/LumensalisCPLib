# from .Manager import MainManager

from ..Identity.Local import NamedLocalIdentifiable
from LumensalisCP.CPTyping import ForwardRef
import LumensalisCP.Main.Manager
from LumensalisCP.common import Debuggable

class MainChild( NamedLocalIdentifiable,Debuggable):
    
    def __init__( self, name:str, main:"LumensalisCP.Main.Manager.MainManager"):
        # type: (str, LumensalisCP.Main.Manager.MainManager ) -> None
        NamedLocalIdentifiable.__init__( self, name = name )
        Debuggable.__init__(self)
        assert main is not None
        self.__main = main
        print( f"MainChild __init__( name={name}, main={main})")
        
    
    @property
    def main(self): return self.__main


class ManagerBase(object):
    
    def __init__(self):
        self._registerManager()
        
    def _registerManager( self ):
        managerClass = self.__class__
        
        # set the unique global instance ... this can be expanded 
        # later to support multiple managers
        existingManager = getattr( managerClass, '_theManager',None)
        if existingManager is not self:
            assert  existingManager is None
            print( f"registering _theManager for {managerClass.__name__}")
            setattr( managerClass, '_theManager', self) 


class SubManagerBase(ManagerBase,MainChild):
    
    def __init__(self, name:str = None, main:"LumensalisCP.Main.Manager.MainManager"=None ):
        ManagerBase.__init__(self)
        MainChild.__init__( self, name=name or self.__class__.__name__, main=main )
        
        self._registerManager()

class ManagerRef(object):
    
    def __init__( self, manager:ManagerBase ):
        assert isinstance(manager,ManagerBase)
        
        # make sure it's the global instance ... this can be expanded 
        # later to support multiple managers
        self.managerClass = managerClass = manager.__class__
        globalManager = getattr( managerClass, '_theManager', None )
        assert manager is globalManager

    def __call__( self ) -> ManagerBase:
        return getattr( self.managerClass, '_theManager', None )

class MainRef(object):
    
    def __init__( self, main:"LumensalisCP.Main.Manager.MainManager"=None  ):
        assert main is LumensalisCP.Main.Manager.MainManager.theManager
        

    def __call__( self ) -> LumensalisCP.Main.Manager.MainManager:
        return LumensalisCP.Main.Manager.MainManager.theManager

