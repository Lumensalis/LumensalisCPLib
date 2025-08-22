# from .Manager import MainManager

from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.common import *
from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl
from LumensalisCP.Temporal.Refreshable import ActivatablePeriodicRefreshable
import LumensalisCP.pyCp.weakref as weakref

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager

#############################################################################
class MainChild( NamedLocalIdentifiable, ActivatablePeriodicRefreshable ):
    
    class KWDS( NamedLocalIdentifiable.KWDS, ActivatablePeriodicRefreshable.KWDS ):
        main: NotRequired[MainManager]
        
    def __init__( self, **kwds:Unpack[KWDS] ):
        main = kwds.pop('main', None) or getMainManager()
        assert main is not None
        
        kwds,nliKwds = NamedLocalIdentifiable.extractInitArgs(kwds)
        NamedLocalIdentifiable.__init__( self, **nliKwds )
        kwds.setdefault( 'autoList', main.refreshables )
        ActivatablePeriodicRefreshable.__init__(self, **kwds)
        
        self.__main = weakref.ref(main)
        # print( f"MainChild __init__( name={self.name}, main={main})")

    @property
    def main(self) -> MainManager:
        return self.__main() # type: ignore
    
    def mcPostCreate(self): pass


#############################################################################
class FactoryBase( MainChild ):
    #def __init__(self, main:MainManager):
    #    super().__init__( main, name=self.__class__.__name__ )

    def makeChild( self, cls:type, **kwds:Any ):
        instance = cls( main=self.main, **kwds )
        self.callPostCreate(instance)
        return instance
    
    def callPostCreate(self, instance:Any):
        instance.mcPostCreate()
        
        
class ManagerBase(CountedInstance):
    
    def __init__(self):
        super().__init__()
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
    
    def __init__(self, **kwds:Unpack[MainChild.KWDS] ):
        ManagerBase.__init__(self)
        MainChild.__init__( self, **kwds )
        
        self._registerManager()

class ManagerRef(CountedInstance):
    
    def __init__( self, manager:ManagerBase ):
        super().__init__()
        assert isinstance(manager,ManagerBase)
        
        # make sure it's the global instance ... this can be expanded 
        # later to support multiple managers
        self.managerClass = managerClass = manager.__class__
        globalManager = getattr( managerClass, '_theManager', None )
        assert manager is globalManager

    def __call__( self ) -> ManagerBase:
        return getattr( self.managerClass, '_theManager', None ) # type: ignore

class MainRef(CountedInstance):
    _theManager:MainManager
    
    def __init__( self, main:MainManager|Any ):
        super().__init__()
        assert main is not None and main is MainRef._theManager

    def __call__( self ) -> MainManager:
        return MainRef._theManager

__all__ = ['MainChild','FactoryBase','ManagerBase','SubManagerBase','ManagerRef','MainRef']
