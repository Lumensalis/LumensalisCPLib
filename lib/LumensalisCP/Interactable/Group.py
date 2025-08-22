from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( __name__, globals() )

# pylint: disable=redefined-builtin,unused-variable,unused-argument,broad-exception-caught
# pyright: reportUnusedImport=false

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import *

from LumensalisCP.Interactable.Interactable import *
from LumensalisCP.Lights.RGB import RGB

_sayImport.parsing()

#############################################################################


INTERACTABLE_BASE = TypeVar('INTERACTABLE_BASE', bound='Interactable')
#############################################################################

class InteractableGroup:
    """ Panels define a collection of controls which can be used to 
     interact with your project

    """
    

    def __init__( self, ) -> None: 
        pass
        #super().__init__( **kwds )

    def _addInteractable( self, controlCls: type,argOne:Optional[Any]=None, 
                     argTwo:Optional[str]=None,
                kind:Optional[str|type]=None,
                kindMatch: Optional[type]=None,
                convertor : Callable[[Any],Any]|None = None,
                defaultStartingValue: Optional[Any]=0.0,
                **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[Any]]
        ) -> Interactable[Any]:

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

        args = self._positionalArgs( controlCls, argOne, argTwo, kwds )
        variable:Interactable[Any] = controlCls( # type: ignore
            *args,
            kind=kind,
            kindMatch=kindMatch,
            convertor=convertor,
            **kwds ) # type: ignore

        return variable

    def _positionalArgs(self, controlCls: type, argOne:Any|None,  argTwo:str|None, kwds:StrAnyDict)->Tuple[Any]:
        return tuple()

    #########################################################################
    def _addZeroToOne( self, controlCls: type, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[ZeroToOne]] ) -> Interactable[ZeroToOne]:
        """ add control for a value between 0 and 1, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addInteractable(  controlCls, argOne, argTwo='ZeroToOne',kindMatch=float,
                                 convertor=lambda v: float(v),   # type: ignore
                                    defaultStartingValue=0.0,
                                    
                                min=0.0, max=1.0, **kwds ) # type: ignore

    def _addPlusMinusOne( self, controlCls: type, argOne:Optional[Any]=None,  argTwo:Optional[str]=None,deadband:Optional[float]=0.1, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[PlusMinusOne]] ) -> Interactable[PlusMinusOne]:
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

        return self._addInteractable( controlCls,argOne, argTwo, kind='PlusMinusOne',kindMatch=float,
                                 convertor=lambda v: float(v),  # type: ignore
                                 defaultStartingValue=0.0,
                                min=-1.0, max=1.0, adjuster=adjuster, **kwds ) # type: ignore


    def _addRGB( self, controlCls: type, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[RGB]] ) -> Interactable[RGB]:
        """ add control for an RGB color value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addInteractable( controlCls, argOne, argTwo, kind='RGB',kindMatch=RGB, convertor=lambda v: RGB.toRGB(v), **kwds ) # type: ignore

    def _addInt( self, controlCls: type, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[int]] ) -> Interactable[int]:
        """ add control for an integer value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addInteractable( controlCls, argOne, argTwo, kind='int', kindMatch=int, convertor=lambda v: int(v), defaultStartingValue=0,**kwds ) # type: ignore

    def _addSwitch( self, controlCls: type, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[bool]] ) -> Interactable[bool]:
        """ add control for a boolean value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addInteractable( controlCls, argOne, argTwo, kind='bool', kindMatch=bool, convertor=lambda v: bool(v), defaultStartingValue=False,**kwds ) # type: ignore

    def _addFloat( self, controlCls: type, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[float]] ) -> Interactable[float]:
        """ add control for a float value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addInteractable( controlCls, argOne, argTwo, kind='float', kindMatch=float, convertor=lambda v: float(v), **kwds ) # type: ignore

    def _addSeconds( self, controlCls: type, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[TimeSpanInSeconds]] ) -> Interactable[TimeSpanInSeconds]:
        """ add control for a duration (in seconds), see  http://lumensalis.com/ql/h2PanelControl """
        return self._addInteractable( controlCls, argOne, argTwo, kind='TimeSpanInSeconds', kindMatch=TimeSpanInSeconds, convertor=lambda v: TimeSpanInSeconds(v), **kwds ) # type: ignore

    def _addMillimeters( self, controlCls: type, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[Millimeters]] ) -> Interactable[Millimeters]:
        """ add control for a distance (in millimeters), see  http://lumensalis.com/ql/h2PanelControl """
        return self._addInteractable( controlCls, argOne, argTwo, kind='Millimeters', kindMatch=Millimeters, convertor=lambda v: Millimeters(v), **kwds ) # type: ignore

    def _addAngle( self, controlCls: type, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[Degrees]] ) -> Interactable[Degrees]:
        """ add control for an angle (in degrees), see  http://lumensalis.com/ql/h2PanelControl """
        return self._addInteractable( controlCls, argOne, argTwo, kind='Degrees', kindMatch=Degrees, convertor=lambda v: Degrees(v), **kwds ) # type: ignore

    #def _addPlusMinusOne( self, controlCls: type, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[PlusMinusOne]] ) -> Interactable[PlusMinusOne]:
    #    """ add control for a float value, see  http://lumensalis.com/ql/h2PanelControl """
    #    return self._addInteractable( controlCls, argOne, argTwo, kind='PlusMinusOne', kindMatch=PlusMinusOne, convertor=lambda v: float(v), **kwds ) # type: ignore

    #def _addZeroToOne( self, controlCls: type, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[ZeroToOne]] ) -> Interactable[ZeroToOne]:
    #    """ add control for a float value, see  http://lumensalis.com/ql/h2PanelControl """
    #    return self._addInteractable( controlCls, argOne, argTwo, kind='ZeroToOne', kindMatch=ZeroToOne, convertor=lambda v: float(v), **kwds ) # type: ignore

    #########################################################################

InteractableGroupT = GenericT(InteractableGroup)

__all__ = [ 'InteractableGroup', 'InteractableGroupT', 'INTERACTABLE_BASE' ]

_sayImport.complete(globals())