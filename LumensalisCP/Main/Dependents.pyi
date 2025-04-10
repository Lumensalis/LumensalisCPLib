# from .Manager import MainManager

from ..Identity.Local import NamedLocalIdentifiable
from LumensalisCP.CPTyping import ForwardRef
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.common import *

class MainChild( NamedLocalIdentifiable):
    
    def __init__( self, name:str, main:MainManager): pass

    main: MainManager

class FactoryBase( object ):
    def __init__(self, main:MainManager):pass
    main: MainManager
    
class ManagerBase(object):
    pass

class SubManagerBase(ManagerBase,MainChild):
    def __init__(self, name:str = None, main:MainManager =None ):pass

class ManagerRef(object):
    
    def __init__( self, manager:ManagerBase ): pass
    def __call__( self ) -> ManagerBase: pass

class MainRef(object):
    
    def __init__( self, main:MainManager  ):pass
    def __call__( self ) -> MainManager: pass

