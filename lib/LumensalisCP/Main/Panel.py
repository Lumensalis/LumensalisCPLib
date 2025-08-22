from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( __name__, globals() )

# pylint: disable=redefined-builtin,unused-variable,unused-argument,broad-exception-caught
# pyright: reportUnusedImport=false

from LumensalisCP.IOContext import *

from LumensalisCP.Main.Dependents import MainChild
from LumensalisCP.Triggers.Trigger import Trigger
from LumensalisCP.Eval.Evaluatable import NamedEvaluatableProtocolT, NamedEvaluatableProtocol


_sayImport.parsing()

#############################################################################
CVT = TypeVar('CVT')
CVT_OUT = TypeVar('CVT_OUT')

class CVT_ADD_KWDS(TypedDict, Generic[CVT,CVT_OUT]):
    startingValue: NotRequired[CVT]
    min: NotRequired[CVT]
    max: NotRequired[CVT]
    name: NotRequired[str]
    description: NotRequired[str]
    
class CVT_KWDS(TypedDict, Generic[CVT,CVT_OUT]):
    startingValue: Required[CVT]
    min: NotRequired[CVT]
    max: NotRequired[CVT]
    name: NotRequired[str]
    description: NotRequired[str]
    kindMatch: NotRequired[type]
    kind: NotRequired[str|type]
    
class PanelControl(InputSource, Generic[CVT, CVT_OUT]):
    
    def __init__(self,  
                 startingValue:CVT,
                 min:Optional[CVT] = None,
                 max:Optional[CVT] = None,
                 description:str="",
                 kind:Optional[str|type]=None,
                 convertor:Optional[Callable[[CVT],CVT_OUT]]=None,
                 kindMatch: Optional[type]=None,
                 adjuster: Optional[Callable[[CVT_OUT], CVT_OUT]] = None,
                 **kwds:Unpack[InputSource.KWDS]
                 ) -> None:
        super().__init__(**kwds)
        name = kwds.get('name', None)
        self.description = description or name
        if kind is None:
            assert startingValue is not None
            kind = type(startingValue).__name__
        self.adjuster = adjuster
        self.kind = kind
        if kindMatch is not None:
            self.kindMatch = kindMatch
        elif isinstance(kind, type):
            self.kindMatch = kind
        elif isinstance( kind, str ): # pyright: ignore
            kType = globals().get(kind,None)
            if isinstance(kType,type):
                self.kindMatch = kType
            else:
                assert kType is None, f"kindMatch for {kind} is not a type: {kType}"

        kType = self.kindMatch        
        assert isinstance(kType, type ), f"kindMatch for {kind} is not a type: {kType}"
        assert kType is not type(None)
        assert kType is not type 

        if convertor is None:
            def convert(v:Any) -> CVT_OUT:
                if isinstance(v,str):
                    v = eval(v)
                if isinstance(v, kType):
                    return v
                return kType(v)
            convertor = convert
        assert convertor is not None

        self.convertor = convertor

        self._min:CVT_OUT|None = convertor(min) if min is not None else None
        self._max:CVT_OUT|None = convertor(max) if max is not None else None
        self._controlValue:CVT_OUT|None = None
        if startingValue is not None:
            self.set( convertor(startingValue) )

    @property
    def controlValue(self) -> CVT_OUT | None:
        return self._controlValue

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
        if isinstance(value, str):
            try:
                value = self.convertor(value) # type: ignore
            except Exception as inst:
                print(f"failed converting {value} to {self.kind} : {inst}")
                return
            
        
        if value != self._controlValue:
            if self.adjuster is not None:
                value = self.adjuster(value)

        if value != self._controlValue:
            if self._min is not None and value < self._min:
                value = self._min
            elif self._max is not None and value > self._max:
                value = self._max
            
            if value != self._controlValue:
                self._controlValue = value
        self.updateValue( UpdateContext.fetchCurrentContext(None) )
    
    def getDerivedValue(self, context:EvaluationContext) -> CVT_OUT|None:
        return self._controlValue
        
    def move( self, delta :Any):
        self.set( self._controlValue + delta )

#############################################################################
class IVT_ADD_KWDS(TypedDict, Generic[CVT]):
    startingValue: NotRequired[CVT]
    min: NotRequired[CVT]
    max: NotRequired[CVT]
    name: NotRequired[str]
    description: NotRequired[str]

class IVT_KWDS(TypedDict, Generic[CVT]):
    startingValue: NotRequired[CVT]
    min: NotRequired[CVT]
    max: NotRequired[CVT]
    name: NotRequired[str]
    description: NotRequired[str]
    kindMatch: NotRequired[type]
    kind: NotRequired[str|type]

class PanelMonitor( NamedLocalIdentifiable, Generic[CVT]   ):
    """ combination of OutputTarget and InputSource

    changes to the OutputTarget (i.e. set)
    :param InputSource: _description_
    :type InputSource: _type_
    :param NamedOutputTarget: _description_
    :type NamedOutputTarget: _type_
    """
    def __init__(self, source:NamedEvaluatableProtocol[CVT], **kwds:Unpack[IVT_KWDS[CVT]] ) -> None:
        super().__init__()
        self.source:NamedEvaluatableProtocol[CVT] = source
        self.__varValue = kwds.pop( 'startingValue', None )
        self.kind = kwds.pop('kind', None)
        self.kindMatch = kwds.pop('kindMatch',  int)
        self._min = kwds.pop('min', None)
        self._max = kwds.pop('max', None)
        self.description = kwds.pop('description', '')

    @property
    def controlValue(self) -> CVT | None:
        return self.__varValue

class PanelPipe( InputSource, OutputTarget,  Generic[CVT] ):
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

class PanelTrigger(Trigger):
    class KWDS(Trigger.KWDS):
        description: NotRequired[str]

    def __init__(self, **kwds:Unpack[KWDS]):
        self.description = kwds.pop('description', '')
        super().__init__(**kwds)


#############################################################################

class ControlPanel( MainChild ):
    """ Panels define a collection of controls which can be used to 
     interact with your project

    """
    def __init__( self, **kwds:Unpack[MainChild.KWDS] ) -> None: 
        super().__init__( **kwds )

        self._controlVariables:NliList[PanelControl[Any,Any]] = NliList(name='controls',parent=self)
        self._monitored:NliList[PanelMonitor[Any]] = NliList(name='monitored',parent=self)
        self._triggers:NliList[PanelTrigger] = NliList(name='triggers',parent=self)

    @property    
    def monitored(self) -> NliList[PanelMonitor[Any]]:
        return self._monitored
    
    @property    
    def controls(self) -> NliList[PanelControl[Any, Any]]:
        return self._controlVariables

    def _addControl( self, argOne:Optional[Any]=None, 
                     argTwo:Optional[str]=None,
                kind:Optional[str|type]=None,
                kindMatch: Optional[type]=None,
                convertor : Callable[[Any],Any]|None = None,
                defaultStartingValue: Optional[Any]=0.0,
                controlCls: type  = PanelControl,
                **kwds:Unpack[CVT_ADD_KWDS[Any,Any]]
        ) -> PanelControl[Any,Any]:

        if isinstance(argOne, str):
            assert 'description' not in kwds, "cannot specify description and argOne as string"
            kwds['description'] = argOne
            argOne = None

        if argTwo is not None:
            assert 'description' not in kwds, "cannot specify description and argTwo as string"
            kwds['description'] = argTwo

        if 'startingValue' not in kwds:
            if argOne is not None:
                assert kindMatch is not None
                assert isinstance(argOne, kindMatch), f"argOne {argOne} is not of type {kindMatch}"
                defaultStartingValue = argOne
            
            assert defaultStartingValue is not None
            min = kwds.get('min', None)
            max = kwds.get('max', None) 
            if min is not None and defaultStartingValue < min:  defaultStartingValue = min
            if max is not None and defaultStartingValue > max:  defaultStartingValue = max
            kwds['startingValue'] = defaultStartingValue

        variable:PanelControl[Any,Any] = controlCls( # type: ignore
            kind=kind,
            kindMatch=kindMatch,
            convertor=convertor,
            **kwds ) # type: ignore
        variable.nliSetContainer(self._controlVariables)
        self.dbgOut( f"added ControlVariable {variable}")
        return variable


    #########################################################################
    def addZeroToOne( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[CVT_ADD_KWDS[float,ZeroToOne]] ) -> PanelControl[float,ZeroToOne]:
        """ add control for a value between 0 and 1, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl(  argOne, argTwo='ZeroToOne',kindMatch=float,
                                 convertor=lambda v: float(v),   # type: ignore
                                    defaultStartingValue=0.0,

                                min=0.0, max=1.0, **kwds ) # type: ignore
    def addPlusMinusOne( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None,deadband:Optional[float]=0.1, **kwds:Unpack[CVT_ADD_KWDS[float,PlusMinusOne]] ) -> PanelControl[float,PlusMinusOne]:
        """ add control for a value between -1 and 1, see  http://lumensalis.com/ql/h2PanelControl """
        adjuster:Callable[[PlusMinusOne], PlusMinusOne] |None

        if deadband is not None:
            def _adjuster(v:PlusMinusOne) -> PlusMinusOne:
                if abs(v) < deadband:
                    return 0.0
                return v
            adjuster = _adjuster
        else:
            adjuster = None

        return self._addControl( argOne, argTwo, kind='PlusMinusOne',kindMatch=float,
                                 convertor=lambda v: float(v),  # type: ignore
                                 defaultStartingValue=0.0,
                                min=-1.0, max=1.0, adjuster=adjuster, **kwds ) # type: ignore

    def addRGB( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[CVT_ADD_KWDS[AnyRGBValue, RGB]] ) -> PanelControl[AnyRGBValue,RGB]:
        """ add control for an RGB color value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl( argOne, argTwo, kind=RGB,convertor=lambda v: RGB.toRGB(v), **kwds ) # type: ignore

    def addInt( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[CVT_ADD_KWDS[int,int]] ) -> PanelControl[int,int]:
        """ add control for an integer value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl( argOne, argTwo, kind=int, convertor=lambda v: int(v), defaultStartingValue=0,**kwds ) # type: ignore

    def addSwitch( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[CVT_ADD_KWDS[bool,bool]] ) -> PanelControl[bool,bool]:
        """ add control for a boolean value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl( argOne, argTwo, kind=bool, convertor=lambda v: bool(v), defaultStartingValue=False,**kwds ) # type: ignore

    def addFloat( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[CVT_ADD_KWDS[float,float]] ) -> PanelControl[float,float]:
        """ add control for a float value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl( argOne, argTwo, kind=float, convertor=lambda v: float(v), **kwds ) # type: ignore

    def addSeconds( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[CVT_ADD_KWDS[TimeSpanInSeconds, TimeSpanInSeconds]] ) -> PanelControl[TimeSpanInSeconds, TimeSpanInSeconds]:
        """ add control for a duration (in seconds), see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl( argOne, argTwo, kind='TimeSpanInSeconds', kindMatch=float, convertor=lambda v: TimeSpanInSeconds(v), **kwds ) # type: ignore

    def addMillimeters( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[CVT_ADD_KWDS[Millimeters,Millimeters]] ) -> PanelControl[Millimeters,Millimeters]:
        """ add control for a distance (in millimeters), see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl( argOne, argTwo, kind='Millimeters', kindMatch=float, convertor=lambda v: Millimeters(v), **kwds ) # type: ignore

    def addAngle( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[CVT_ADD_KWDS[Degrees,Degrees]] ) -> PanelControl[Degrees,Degrees]:
        """ add control for an angle (in degrees), see  http://lumensalis.com/ql/h2PanelControl """
        return self._addControl( argOne, argTwo, kind='Degrees', kindMatch=float, convertor=lambda v: Degrees(v), **kwds ) # type: ignore

    def addTrigger( self, argTwo:Optional[str]=None, **kwds:Unpack[PanelTrigger.KWDS] ) -> PanelTrigger:
        if argTwo is not None:
            assert 'description' not in kwds, "cannot specify description and argTwo as string"
            kwds['description'] = argTwo
        trigger = PanelTrigger(**kwds)
        self._triggers.append(trigger)
        return trigger

    #########################################################################
    def _addMonitor( self,
                input:NamedEvaluatableProtocol[Any],
                kind:str|type,
                kindMatch: Optional[type]=None,
                convertor : Callable[[Any],Any]|None = None,
                **kwds:Unpack[IVT_ADD_KWDS[Any]],
        ) -> PanelMonitor[Any]:
        variable:PanelMonitor[Any] 
        variable = PanelMonitor( input, **kwds )
        variable.nliSetContainer(self._monitored)
        self.dbgOut( f"added Monitor {variable} ({type(variable)})")
        return variable
    
    #########################################################################
    def monitorZeroToOne( self, input:NamedEvaluatableProtocol[ZeroToOne],**kwds:Unpack[IVT_ADD_KWDS[ZeroToOne]] ) -> PanelMonitor[ZeroToOne]:
        """ add monitor for a value between 0 and 1, see  http://lumensalis.com/ql/h2PanelMonitor """
        return self._addMonitor(  input, kind='ZeroToOne', kindMatch=float, **kwds )

    def monitorRGB( self, input:NamedEvaluatableProtocol[RGB],**kwds:Unpack[IVT_ADD_KWDS[RGB]] ) -> PanelMonitor[RGB]:
        """ add monitor for a RGB color value, see  http://lumensalis.com/ql/h2PanelMonitor """
        return self._addMonitor(  input, kind=RGB, **kwds )

    def monitorInt( self, input:NamedEvaluatableProtocol[int],**kwds:Unpack[IVT_ADD_KWDS[int]] ) -> PanelMonitor[int]:
        """ add monitor for an integer value, see  http://lumensalis.com/ql/h2PanelMonitor """
        return self._addMonitor(  input, kind=int, **kwds )

    def monitorFloat( self, input:NamedEvaluatableProtocol[float],**kwds:Unpack[IVT_ADD_KWDS[float]] ) -> PanelMonitor[float]:
        """ add monitor for a float value, see  http://lumensalis.com/ql/h2PanelMonitor """
        return self._addMonitor(  input, kind=float, **kwds )

    def monitorSeconds( self, input:NamedEvaluatableProtocol[TimeInSeconds],**kwds:Unpack[IVT_ADD_KWDS[TimeInSeconds]] ) -> PanelMonitor[TimeInSeconds]:
        """ add monitor for a duration (in seconds), see  http://lumensalis.com/ql/h2PanelMonitor """
        return self._addMonitor(  input, kind='TimeInSeconds', kindMatch=float, **kwds )

    def monitorMillimeters( self, input:NamedEvaluatableProtocol[Millimeters],**kwds:Unpack[IVT_ADD_KWDS[Millimeters]] ) -> PanelMonitor[Millimeters]:
        """ add monitor for a distance (in millimeters), see  http://lumensalis.com/ql/h2PanelMonitor """
        return self._addMonitor(  input, kind='Millimeters', kindMatch=float, **kwds )
    
    def monitorAngle( self, input:NamedEvaluatableProtocol[Degrees],**kwds:Unpack[IVT_ADD_KWDS[Degrees]] ) -> PanelMonitor[Degrees]:
        """ add monitor for an angle (in degrees), see  http://lumensalis.com/ql/h2PanelMonitor """        
        return self._addMonitor(  input, kind='Degrees', kindMatch=float, **kwds )
    
    def monitor( self, input:NamedEvaluatableProtocol[Any],**kwds:Unpack[IVT_ADD_KWDS[Any]] ) -> PanelMonitor[Any]:
        """ add monitor for generic input, see  http://lumensalis.com/ql/h2PanelMonitor """        
        return self._addMonitor(  input, kind='Any', **kwds )
    
    #########################################################################


    def nliGetContainers(self) -> Iterable[NliContainerMixin[PanelControl[Any, Any]]]:
        yield self._controlVariables
        
__all__ = [ 'ControlPanel', 'PanelControl', 'PanelMonitor' ]

_sayImport.complete(globals())