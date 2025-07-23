from LumensalisCP.IOContext import *

from LumensalisCP.Main.Dependents import MainChild

# pylint: disable=redefined-builtin,unused-variable,unused-argument,broad-exception-caught

#############################################################################

class ControlVariable(InputSource):
    class KWDS(TypedDict):
        startingValue: Required[Any]
        min: NotRequired[Any]
        max: NotRequired[Any]
        name: NotRequired[str]
        description: NotRequired[str]
        kind: NotRequired[str|type]
        
    def __init__(self,  
                 startingValue:Any,
                 min:Optional[Any] = None,
                 max:Optional[Any] = None,
                 name:Optional[str]=None,
                 description:str="",
                 kind:Optional[str|type]=None,
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
    
    def setFromWs( self, value: Any ):
        if self.kind == 'RGB':
            if isinstance(value, str):
                try:
                    rgb = ( int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16) )
                    value = rgb
                    # print( f"rgb converted {value} to {rgb}" )
                except Exception as inst:
                    print( f"failed converting {value} to RGB : {inst}" )
                
        self.set( value )
        
    def set( self, value: Any ):
        if value != self._controlValue:
            if self._min is not None and value < self._min:
                value = self._min
            elif self._max is not None and value > self._max:
                value = self._max
            
            if value != self._controlValue:
                self._controlValue = value
    
    def getDerivedValue(self, context:EvaluationContext) -> Any:
        return self._controlValue
        
    def move( self, delta :Any):
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
        
        
    def getDerivedValue(self, context:EvaluationContext) -> Any:
        return self.__varValue
    
    def set( self, value:Any, context:Optional[EvaluationContext]=None ):
        self.__varValue = value
        self.updateValue( UpdateContext.fetchCurrentContext(context) )
    
#############################################################################

class ControlPanel( MainChild ):
    
    def __init__( self, main:'LumensalisCP.Main.Manager.MainManager', name:Optional[str]=None ): # type: ignore[no-untyped-def]
        super().__init__( main=main, name=name )

        self._controlVariables:NliList[ControlVariable] = NliList(name='controlVariables',parent=self)
        
    def addControlVariable( self, **kwds:Unpack[ControlVariable.KWDS] ) -> ControlVariable:
        variable = ControlVariable( **kwds )
        variable.nliSetContainer(self._controlVariables)
        self.infoOut( f"added ControlVariable {variable}")
        return variable

    def addIntermediateVariable( self, *args, **kwds ) -> IntermediateVariable:
        variable = IntermediateVariable( *args,**kwds )
        variable.nliSetContainer(self._controlVariables)
        self.infoOut( f"added Variable {variable}")
        variable.updateValue( self.main.getContext() )
        return variable

    def nliGetContainers(self) -> Iterable[NliContainerMixin]|None:
        yield self._controlVariables
        
__all__ = [ 'ControlPanel', 'ControlVariable', 'IntermediateVariable' ]
