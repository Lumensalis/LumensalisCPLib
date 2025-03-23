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
    
    
class NamedLocalIdentifiable(LocalIdentifiable):
    def __init__( self, name:str=None ):
        assert name is not None
        self._name = name
        super().__init__()
        
    name = property( lambda self: self._name )