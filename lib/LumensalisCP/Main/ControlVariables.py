from LumensalisCP.Audio import MainChild
from LumensalisCP.Identity.Local import NamedLocalIdentifiableList, NamedLocalIdentifiableContainerMixin
import LumensalisCP.Main
from LumensalisCP.Inputs import InputSource
from LumensalisCP.Main.Expressions import  EvaluationContext
 
from LumensalisCP.Main.Updates import UpdateContext
from LumensalisCP.Outputs import OutputTarget, NamedOutputTarget
from LumensalisCP.CPTyping  import *
import LumensalisCP.Main

class ControlVariable(InputSource):
    
    def __init__(self,  startingValue=None,
                 min = None, max = None,
                 name:Optional[str]=None, description:str="", kind:Optional[str]=None,
                 ):
        super().__init__(name)
        self.description = description or name
        if kind is None:
            assert startingValue is not None
            kind = type(startingValue).__name__
                
        self.kind = kind
        
        self._min = min
        self._max = max
        self._controlValue = None
        if startingValue is not None:
            self.set( startingValue )

    controlValue = property( lambda self: self._controlValue )
    
    def setFromWs( self, value ):
        if self.kind == 'RGB':
            if type(value) == str:
                try:
                    rgb = ( int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16) )
                    value = rgb
                    # print( f"rgb converted {value} to {rgb}" )
                except Exception as inst:
                    print( f"failed converting {value} to RGB" )
                
        self.set( value )
        
    def set( self, value ):
        if value != self._controlValue:
            if self._min is not None and value < self._min:
                value = self._min
            elif self._max is not None and value > self._max:
                value = self._max
            
            if value != self._controlValue:
                self._controlValue = value
    
    def getDerivedValue(self, context:UpdateContext) -> bool:
        return self._controlValue == True
        
    def move( self, delta ):
        self.set( self._controlValue + delta )

#############################################################################

class IntermediateVariable( InputSource, OutputTarget ):
    """ combination of OutputTarget and InputSource

    changes to the OutputTarget (i.e. set)
    :param InputSource: _description_
    :type InputSource: _type_
    :param NamedOutputTarget: _description_
    :type NamedOutputTarget: _type_
    """
    def __init__(self, name:str, value:Any = None ):
        InputSource.__init__(self,name=name)
        OutputTarget.__init__(self)
        self.__varValue = value
        
        
    def getDerivedValue(self, context:UpdateContext) -> Any:
        return self.__varValue
    
    def set( self, value:Any, context:Optional[EvaluationContext]=None ):
        self.__varValue = value
        self.updateValue( UpdateContext.fetchCurrentContext(context) )
    
#############################################################################

class Controller( MainChild ):
    
    def __init__( self, main:"LumensalisCP.Main.Manager.MainManager", name:Optional[str]=None ):
        super().__init__( main=main, name=name )

        self._controlVariables = NamedLocalIdentifiableList(name='controlVariables',parent=self)
        
    def addControlVariable( self, *args, **kwds ) -> ControlVariable:
        variable = ControlVariable( *args,**kwds )
        variable.nliSetContainer(self._controlVariables)
        self.infoOut( f"added ControlVariable {variable}")
        return variable

    def addIntermediateVariable( self, *args, **kwds ) -> IntermediateVariable:
        variable = IntermediateVariable( *args,**kwds )
        variable.nliSetContainer(self._controlVariables)
        self.infoOut( f"added Variable {variable}")
        variable.updateValue( self.main.getContext() )
        return variable

    def nliGetContainers(self) -> Iterable[NamedLocalIdentifiableContainerMixin]|None:
        yield self._controlVariables
        
__all__ = [ Controller, ControlVariable, IntermediateVariable ]