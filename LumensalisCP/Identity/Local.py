from ..Debug import Debuggable

class LocalIdentifiable(object):
    
    __nextId = 1
    
    @staticmethod
    def __getNextId( self2 ):
        # TODO : thread safe / groups
        id = LocalIdentifiable.__nextId
        LocalIdentifiable.__nextId += 1

    def __init__( self ):
        self.__localId = self.__getNextId(self)
        
    localId = property( lambda self: self.__localId )
    
    
class NamedLocalIdentifiable(LocalIdentifiable,Debuggable):
    def __init__( self, name:str=None ):
        assert name is not None
        self.__name = name
        LocalIdentifiable.__init__(self)
        Debuggable.__init__(self)
        
    @property
    def name(self) -> str: return self.__name
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__name}:{self.localId})"