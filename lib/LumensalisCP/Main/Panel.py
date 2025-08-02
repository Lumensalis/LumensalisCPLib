from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( "Main.Panel" )

from LumensalisCP.IOContext import *

from LumensalisCP.Main.Dependents import MainChild

# pylint: disable=redefined-builtin,unused-variable,unused-argument,broad-exception-caught

_sayImport.parsing()

#############################################################################
CVT = TypeVar('CVT')
CVT_OUT = TypeVar('CVT_OUT')

class CVT_KWDS(TypedDict, Generic[CVT,CVT_OUT]):
    startingValue: Required[CVT]
    min: NotRequired[CVT]
    max: NotRequired[CVT]
    name: NotRequired[str]
    description: NotRequired[str]
    
class PanelControl(InputSource, Generic[CVT, CVT_OUT]):
    
    def __init__(self,  
                 startingValue:CVT,
                 min:Optional[CVT] = None,
                 max:Optional[CVT] = None,
                 description:str="",
                 kind:Optional[str|type]=None,
                 convertor:Optional[Callable[[CVT],CVT_OUT]]=None,
                 kindMatch: Optional[type]=None,
                 **kwds:Unpack[InputSource.KWDS]
                 ) -> None:
        super().__init__(**kwds)
        name = kwds.get('name', None)
        self.description = description or name
        if kind is None:
            assert startingValue is not None
            kind = type(startingValue).__name__
                
        self.kind = kind
        self.kindMatch = kindMatch or type if isinstance(kind, str) else kind

        if convertor is None:
            convertor = lambda v: v # type: ignore
        assert convertor is not None

        self.convertor = convertor

        self._min:CVT_OUT|None = convertor(min) if min is not None else None
        self._max:CVT_OUT|None = convertor(max) if max is not None else None
        self._controlValue:CVT_OUT|None = None
        if startingValue is not None:
            self.set( convertor(startingValue) )

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
    
    def getDerivedValue(self, context:EvaluationContext) -> CVT_OUT|None:
        return self._controlValue
        
    def move( self, delta :Any):
        self.set( self._controlValue + delta )

#############################################################################
class IVT_KWDS(TypedDict, Generic[CVT]):
    startingValue: NotRequired[CVT]
    min: NotRequired[CVT]
    max: NotRequired[CVT]
    name: NotRequired[str]
    description: NotRequired[str]

class PanelMonitor( NamedLocalIdentifiable, Generic[CVT]   ):
    """ combination of OutputTarget and InputSource

    changes to the OutputTarget (i.e. set)
    :param InputSource: _description_
    :type InputSource: _type_
    :param NamedOutputTarget: _description_
    :type NamedOutputTarget: _type_
    """
    def __init__(self, source:InputSource, **kwds:Unpack[IVT_KWDS[CVT]] ) -> None:
        super().__init__()
        self.source = source
        self.__varValue = kwds.pop( 'startingValue', None )
        self.kind = kwds.pop('kind', None)
        self.kindMatch = kwds.pop('kindMatch', None)
        self._min = kwds.pop('min', None)
        self._max = kwds.pop('max', None)
        self.description = kwds.pop('description', '')

class PanelPipe( InputSource,  Generic[CVT], OutputTarget ):
    """ combination of OutputTarget and InputSource

    changes to the OutputTarget (i.e. set) 
    :param InputSource: _description_
    :type InputSource: _type_
    :param NamedOutputTarget: _description_
    :type NamedOutputTarget: _type_
    """
    def __init__(self, **kwds:Unpack[IVT_KWDS[CVT]] ) -> None:
        self.__varValue = kwds.pop( 'startingValue', None )
        self.kind = kwds.pop('kind', None)
        self.kindMatch = kwds.pop('kindMatch', None)
        self._min = kwds.pop('min', None)
        self._max = kwds.pop('max', None)
        self.description = kwds.pop('description', '')
        InputSource.__init__(self,**kwds ) # type: ignore
        OutputTarget.__init__(self)
        
        
        
    def getDerivedValue(self, context:EvaluationContext) -> CVT|None:
        return self.__varValue
    
    def set( self, value:CVT, context:Optional[EvaluationContext]=None ) -> None:
        self.__varValue = value
        self.updateValue( UpdateContext.fetchCurrentContext(context) )

#############################################################################

class ControlPanel( MainChild ):
    """ Panels define a collection of controls which can be used to 
     interact with your project

    """
    def __init__( self, **kwds:Unpack[MainChild.KWDS] ) -> None: 
        super().__init__( **kwds )

        self._controlVariables:NliList[PanelControl[Any,Any]] = NliList(name='controls',parent=self)
        self._monitored:NliList[PanelMonitor[Any]] = NliList(name='monitored',parent=self)

    @property    
    def monitored(self) -> NliList[PanelMonitor[Any]]:
        return self._monitored
    
    @property    
    def controls(self) -> NliList[PanelControl[Any, Any]]:
        return self._controlVariables

    def _addControl( self,
                kind:Optional[str|type]=None,
                kindMatch: Optional[type]=None,
                convertor : Callable[[Any],Any]|None = None,
                **kwds:Unpack[CVT_KWDS[Any,Any]]
        ) -> PanelControl[Any,Any]:

          
        variable:PanelControl[Any,Any] = PanelControl( 
            kind=kind,
            kindMatch=kindMatch,
            convertor=convertor,
            **kwds )
        variable.nliSetContainer(self._controlVariables)
        self.dbgOut( f"added ControlVariable {variable}")
        return variable


    #########################################################################
    def addZeroToOne( self, **kwds:Unpack[CVT_KWDS[float,ZeroToOne]] ) -> PanelControl[float,ZeroToOne]:
        """ add control for a value between 0 and 1, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl(  kind='ZeroToOne',kindMatch=float, convertor=lambda v: float(v), **kwds )

    def addRGB( self, **kwds:Unpack[CVT_KWDS[AnyRGBValue, RGB]] ) -> PanelControl[AnyRGBValue,RGB]:
        """ add control for an RGB color value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl(  kind=RGB,convertor=lambda v: RGB.toRGB(v), **kwds )

    def addInt( self, **kwds:Unpack[CVT_KWDS[int,int]] ) -> PanelControl[int,int]:
        """ add control for an integer value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl(  kind=int, convertor=lambda v: int(v), **kwds )

    def addFloat( self, **kwds:Unpack[CVT_KWDS[float,float]] ) -> PanelControl[float,float]:
        """ add control for a float value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl(  kind=float, convertor=lambda v: float(v), **kwds )

    def addSeconds( self, **kwds:Unpack[CVT_KWDS[TimeSpanInSeconds, TimeSpanInSeconds]] ) -> PanelControl[TimeSpanInSeconds, TimeSpanInSeconds]:
        """ add control for a duration (in seconds), see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl(  kind='TimeSpanInSeconds', kindMatch=float, convertor=lambda v: TimeSpanInSeconds(v), **kwds )

    def addMillimeters( self, **kwds:Unpack[CVT_KWDS[Millimeters,Millimeters]] ) -> PanelControl[Millimeters,Millimeters]:
        """ add control for a distance (in millimeters), see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl(  kind='Millimeters', kindMatch=float, convertor=lambda v: Millimeters(v), **kwds )

    def addAngle( self, **kwds:Unpack[CVT_KWDS[Degrees,Degrees]] ) -> PanelControl[Degrees,Degrees]:
        """ add control for an angle (in degrees), see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl(  kind='Degrees', kindMatch=float, convertor=lambda v: Degrees(v), **kwds )

    #########################################################################
    def _addMonitor( self,
                input:InputSource,
                kind:str|type,
                kindMatch: Optional[type]=None,
                convertor : Callable[[Any],Any]|None = None,
                **kwds:Unpack[IVT_KWDS[Any]],
        ) -> PanelMonitor[Any]:
        variable:PanelMonitor[Any] 
        variable = PanelMonitor( input, **kwds )
        variable.nliSetContainer(self._monitored)
        self.dbgOut( f"added Monitor {variable} ({type(variable)})")
        return variable
    
    #########################################################################
    def monitorZeroToOne( self, input:InputSource,**kwds:Unpack[IVT_KWDS[ZeroToOne]] ) -> PanelMonitor[ZeroToOne]:
        """ add monitor for a value between 0 and 1, see  http://lumensalis.com/ql/h2PanelMonitor """
        return self._addMonitor(  input, kind='ZeroToOne', kindMatch=float, **kwds )

    def monitorRGB( self, input:InputSource,**kwds:Unpack[IVT_KWDS[RGB]] ) -> PanelMonitor[RGB]:
        """ add monitor for a RGB color value, see  http://lumensalis.com/ql/h2PanelMonitor """
        return self._addMonitor(  input, kind=RGB, **kwds )

    def monitorInt( self, input:InputSource,**kwds:Unpack[IVT_KWDS[int]] ) -> PanelMonitor[int]:
        """ add monitor for an integer value, see  http://lumensalis.com/ql/h2PanelMonitor """
        return self._addMonitor(  input, kind=int, **kwds )

    def monitorFloat( self, input:InputSource,**kwds:Unpack[IVT_KWDS[float]] ) -> PanelMonitor[float]:
        """ add monitor for a float value, see  http://lumensalis.com/ql/h2PanelMonitor """
        return self._addMonitor(  input, kind=float, **kwds )

    def monitorSeconds( self, input:InputSource,**kwds:Unpack[IVT_KWDS[TimeInSeconds]] ) -> PanelMonitor[TimeInSeconds]:
        """ add monitor for a duration (in seconds), see  http://lumensalis.com/ql/h2PanelMonitor """
        return self._addMonitor(  input, kind='TimeInSeconds', kindMatch=float, **kwds )

    def monitorMillimeters( self, input:InputSource,**kwds:Unpack[IVT_KWDS[Millimeters]] ) -> PanelMonitor[Millimeters]:
        """ add monitor for a distance (in millimeters), see  http://lumensalis.com/ql/h2PanelMonitor """
        return self._addMonitor(  input, kind='Millimeters', kindMatch=float, **kwds )
    
    def monitorAngle( self, input:InputSource,**kwds:Unpack[IVT_KWDS[Degrees]] ) -> PanelMonitor[Degrees]:
        """ add monitor for an angle (in degrees), see  http://lumensalis.com/ql/h2PanelMonitor """        
        return self._addMonitor(  input, kind='Degrees', kindMatch=float, **kwds )
    
    def monitor( self, input:InputSource,**kwds:Unpack[IVT_KWDS[Any]] ) -> PanelMonitor[Any]:
        """ add monitor for generic input, see  http://lumensalis.com/ql/h2PanelMonitor """        
        return self._addMonitor(  input, kind='Any', **kwds )
    
    #########################################################################


    def nliGetContainers(self) -> Iterable[NliContainerMixin[PanelControl[Any, Any]]]|None:
        yield self._controlVariables
        
__all__ = [ 'ControlPanel', 'PanelControl', 'PanelMonitor' ]

_sayImport.complete(globals())