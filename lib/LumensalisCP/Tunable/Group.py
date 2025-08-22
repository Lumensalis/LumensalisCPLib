from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( __name__, globals() )

# pylint: disable=redefined-builtin,unused-variable,unused-argument,broad-exception-caught
# pyright: reportUnusedImport=false

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import *

from LumensalisCP.Interactable.Interactable import *
from LumensalisCP.Interactable.Group import *
from LumensalisCP.Tunable.Tunable import *
from LumensalisCP.Tunable.Tunables import *

_sayImport.parsing()

#############################################################################

class TunableGroup( Tunable, NamedLocalIdentifiable, InteractableGroup ):
    """ Panels define a collection of controls which can be used to 
     interact with your project

    """

    def __init__( self, **kwds:Unpack[NamedLocalIdentifiable.KWDS] ) -> None: 
        Tunable.__init__( self )
        NamedLocalIdentifiable.__init__( self, **kwds )

        self._tunables:NliList[TunableSetting[Any,TunableGroup]] = NliList(name='tunables',parent=self)

    @property
    def tunables(self) -> NliList[TunableSetting[Any,TunableGroup]]:
        return self._tunables

    def _positionalArgs(self, controlCls: type, argOne:Any|None,  argTwo:str|None, kwds:StrAnyDict)->Tuple[Any]:
        defaultStartingValue = kwds.get('startingValue', None)
        assert defaultStartingValue is not None
        return (defaultStartingValue,)
    
    #def addRGB( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[CVT_ADD_KWDS[AnyRGBValue, RGB]] ) -> PanelControl[AnyRGBValue,RGB]:
    #    """ add control for an RGB color value, see  http://lumensalis.com/ql/h2PanelControl """
    #    return self._addControl( argOne, argTwo, kind=RGB,convertor=lambda v: RGB.toRGB(v), **kwds ) # type: ignore

    def addInt( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[int]] ) -> IntSetting:
        """ add control for an integer value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addInt( IntSetting, argOne, argTwo, **kwds ) # type: ignore

    def addSwitch( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[bool]] ) -> BoolSetting:
        """ add control for a boolean value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addSwitch( BoolSetting, argOne, argTwo, **kwds ) # type: ignore

    def addFloat( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[float]] ) -> FloatSetting:
        """ add control for a float value, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addFloat( FloatSetting, argOne, argTwo,  **kwds ) # type: ignore

    def addSeconds( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[TimeSpanInSeconds]] ) -> SecondsSetting:
        """ add control for a duration (in seconds), see  http://lumensalis.com/ql/h2PanelControl """
        return self._addSeconds( SecondsSetting, argOne, argTwo,  **kwds ) # type: ignore

    def addMillimeters( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[Millimeters]] ) -> MillimetersSetting:
        """ add control for a distance (in millimeters), see  http://lumensalis.com/ql/h2PanelControl """
        return self._addMillimeters( MillimetersSetting, argOne, argTwo,  **kwds ) # type: ignore

    def addAngle( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[Degrees]] ) -> DegreesSetting:
        """ add control for an angle (in degrees), see  http://lumensalis.com/ql/h2PanelControl """
        return self._addAngle( DegreesSetting, argOne, argTwo,  **kwds ) # type: ignore

    def addZeroToOne( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[ZeroToOne]] ) -> ZeroToOneSetting:
        """ add control for a value between 0 and 1, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addZeroToOne( ZeroToOneSetting, argOne, argTwo,  **kwds ) # type: ignore

    def addPlusMinusOne( self, argOne:Optional[Any]=None,  argTwo:Optional[str]=None, **kwds:Unpack[INTERACTABLE_ARG_T_ADD_KWDS[PlusMinusOne]] ) -> PlusMinusOneSetting:
        """ add control for a value between -1 and 1, see  http://lumensalis.com/ql/h2PanelControl """
        return self._addPlusMinusOne( PlusMinusOneSetting, argOne, argTwo,  **kwds ) # type: ignore

    #########################################################################


    def nliGetContainers(self) -> Iterable[NliContainerMixin[TunableSetting[Any,TunableGroup]]]:
        yield self._tunables

    def nliHasContainers(self) -> bool:
        return True
        
__all__ = [ 'TunableGroup' ]

_sayImport.complete(globals())