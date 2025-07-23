# from .Manager import MainManager

from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.common import *
from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl
import LumensalisCP.pyCp.weakref as weakref

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager

#############################################################################
class MainChild( NamedLocalIdentifiable ):
    
    def __init__( self, main:Optional[MainManager]=None, name:Optional[str]=None ):
        NamedLocalIdentifiable.__init__( self, name = name or self.__class__.__name__)
        main = main or getMainManager()
        ensure( main is not None )
        self.__main = weakref.ref(main)
        # print( f"MainChild __init__( name={self.name}, main={main})")

    @property
    def main(self) -> MainManager:
        return self.__main() # type: ignore
    
    def mcPostCreate(self): pass


#############################################################################
class FactoryBase( MainChild ):
    def __init__(self, main:MainManager):
        super().__init__( main, name=self.__class__.__name__ )

    def makeChild( self, cls:type, **kwds:StrAnyDict ):
        instance = cls( main=self.main, **kwds )
        self.callPostCreate(instance)
        return instance
    
    def callPostCreate(self, instance:Any):
        instance.mcPostCreate()
        
        
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
            if pmc_mainLoopControl.preMainVerbose: print( f"registering _theManager for {managerClass.__name__}")
            setattr( managerClass, '_theManager', self) 


class SubManagerBase(ManagerBase,MainChild):
    
    def __init__(self, main:MainManager, name:Optional[str] = None ):
        ManagerBase.__init__(self)
        MainChild.__init__( self, main=main, name=name )
        
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
        return getattr( self.managerClass, '_theManager', None ) # type: ignore

class MainRef(object):
    _theManager:MainManager
    
    def __init__( self, main:MainManager|Any ):
        assert main is not None and main is MainRef._theManager

    def __call__( self ) -> MainManager:
        return MainRef._theManager

__all__ = ['MainChild','FactoryBase','ManagerBase','SubManagerBase','ManagerRef','MainRef']
