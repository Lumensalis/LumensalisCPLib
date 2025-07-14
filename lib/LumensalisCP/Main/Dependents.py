# from .Manager import MainManager

from ..Identity.Local import NamedLocalIdentifiable
from LumensalisCP.CPTyping import *
from LumensalisCP.common import *

#############################################################################
class MainChild( NamedLocalIdentifiable ):
    
    def __init__( self, name:str, main):
        # type: (str, LumensalisCP.Main.Manager.MainManager ) -> None
        NamedLocalIdentifiable.__init__( self, name = name or self.__class__.__name__)
        ensure( main is not None )
        self.__main = weakref.ref(main)
        # print( f"MainChild __init__( name={self.name}, main={main})")

    @property
    def main(self): return self.__main()
    
    def mcPostCreate(self): pass

#############################################################################
class FactoryBase( MainChild ):
    def __init__(self, main:"LumensalisCP.Main.Manager.MainManager"):
        super().__init__( self.__class__.__name__, main )

    def makeChild( self, cls, **kwds ):
        instance = cls( main=self.main, **kwds )
        self.callPostCreate(instance)
        return instance
    
    def callPostCreate(self, instance):
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
    _theManager:"LumensalisCP.Main.Manager.MainManager" = None
    
    def __init__( self, main:"LumensalisCP.Main.Manager.MainManager"=None  ):
        assert main is not None and main is MainRef._theManager

    def __call__( self ) -> LumensalisCP.Main.Manager.MainManager:
        return MainRef._theManager

