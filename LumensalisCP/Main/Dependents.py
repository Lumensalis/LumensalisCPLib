# from .Manager import MainManager

from ..Identity.Local import NamedLocalIdentifiable
from LumensalisCP.CPTyping import ForwardRef
import LumensalisCP.Main.Manager

class MainChild( NamedLocalIdentifiable ):
    
    def __init__( self, name:str, main:"LumensalisCP.Main.Manager.MainManager"):
        # type: (str, LumensalisCP.Main.Manager.MainManager ) -> None
        super().__init__( name = name )
        self.__main = main
        print( f"MainChild __init__( name={name}, main={main})")
        
    
    @property
    def main(self): return self.__main
