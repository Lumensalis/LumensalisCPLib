from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__profileImport = getImportProfiler( __name__, globals() ) 

# pyright: reportUnusedImport=false, reportPrivateUsage=false

from LumensalisCP.Eval.Expressions import *
from LumensalisCP.Outputs import NamedNotifyingOutputTarget, NotifyingOutputTargetT,OutputTarget
from LumensalisCP.Interactable.Interactable import Interactable, InteractableT, INTERACTABLE_ARG_T, INTERACTABLE_T

from LumensalisCP.Tunable.Tunable import *
from LumensalisCP.Tunable.TunableKWDS import *

#############################################################################

__profileImport.parsing()

#############################################################################

class TunableIntSetting(TunableSettingT[int,TUNABLE_SELF_T]):
    TUNABLE_DEFAULTS:ClassVar[StrAnyDict] = {'kind': int, 'kindMatch': int}

TunableIntSettingT = GenericT(TunableIntSetting)

class IntSetting(TunableIntSettingT[Tunable]): ...

class TunableIntDescriptor(TunableDescriptorT[IntSetting,Tunable]):
    SETTING_CLASS = IntSetting

def tunableInt(  default:int, 
        **kwds:Unpack[TUNABLE_SETTING_KWDS[int,TUNABLE_SELF_T]]
    ) -> Callable[
        [   Callable[[TUNABLE_SELF_T, IntSetting, EvaluationContext],
             None]],
        TunableIntDescriptor]:
    return tunableProperty( default, TunableIntDescriptor, **kwds) # type: ignore
#############################################################################

class TunableZeroToOneSetting(TunableSettingT[ZeroToOne,TUNABLE_SELF_T]):
    TUNABLE_DEFAULTS:ClassVar[StrAnyDict] = {'kind': ZeroToOne, 'kindMatch': ZeroToOne, 'min': ZeroToOne(0.0), 'max': ZeroToOne(1.0)}

TunableZeroToOneSettingT = GenericT(TunableZeroToOneSetting)

class ZeroToOneSetting(TunableZeroToOneSettingT[Tunable]): ...

class TunableZeroToOneDescriptor(TunableDescriptorT[ZeroToOne,Tunable]):
    SETTING_CLASS = ZeroToOneSetting

def tunableZeroToOne(  default:ZeroToOne, 
        **kwds:Unpack[TUNABLE_SETTING_KWDS[ZeroToOne,TUNABLE_SELF_T]]
    ) -> Callable[
        [   Callable[[TUNABLE_SELF_T, ZeroToOneSetting, EvaluationContext],
             None]], 
        TunableZeroToOneDescriptor]:
    return tunableProperty( default, TunableZeroToOneDescriptor, **kwds) # type: ignore

#############################################################################

class TunablePlusMinusOneSetting(TunableSettingT[PlusMinusOne,TUNABLE_SELF_T]):
    TUNABLE_DEFAULTS:ClassVar[StrAnyDict] = {'kind': PlusMinusOne, 'kindMatch': PlusMinusOne, 'min': PlusMinusOne(-1.0), 'max': PlusMinusOne(1.0)}

TunablePlusMinusOneSettingT = GenericT(TunablePlusMinusOneSetting)

class PlusMinusOneSetting(TunablePlusMinusOneSettingT[Tunable]): ...

class TunablePlusMinusOneDescriptor(TunableDescriptorT[PlusMinusOne,Tunable]):
    SETTING_CLASS = PlusMinusOneSetting

def tunablePlusMinusOne(  default:PlusMinusOne,
        **kwds:Unpack[TUNABLE_SETTING_KWDS[PlusMinusOne,TUNABLE_SELF_T]]
    ) -> Callable[
        [   Callable[[TUNABLE_SELF_T,PlusMinusOneSetting,EvaluationContext],
                      None]], 
             TunablePlusMinusOneDescriptor]:
    return tunableProperty( default, TunablePlusMinusOneDescriptor, **kwds) # type: ignore

tunablePlusMinusOneT = GenericT(tunablePlusMinusOne)
#############################################################################


#############################################################################

class TunableBoolSetting(TunableSettingT[bool,TUNABLE_SELF_T]):
    TUNABLE_DEFAULTS:ClassVar[StrAnyDict] = {'kind': bool, 'kindMatch': bool}

TunableBoolSettingT = GenericT(TunableBoolSetting)

class BoolSetting(TunableBoolSettingT[Tunable]): ... 
class TunableBoolDescriptor(TunableDescriptorT[bool,Tunable]):
    SETTING_CLASS = BoolSetting
def tunableBool(  default:bool,
        **kwds:Unpack[TUNABLE_SETTING_KWDS[bool,TUNABLE_SELF_T]]
    ) -> Callable[
        [   Callable[[TUNABLE_SELF_T, BoolSetting, EvaluationContext],
             None]],
        TunableBoolDescriptor]:
    return tunableProperty( default, TunableBoolDescriptor, **kwds) # type: ignore

#############################################################################

class TunableFloatSetting(TunableSettingT[float,TUNABLE_SELF_T]):
    TUNABLE_DEFAULTS:ClassVar[StrAnyDict] = {'kind': float, 'kindMatch': float}

TunableFloatSettingT = GenericT(TunableFloatSetting)
class FloatSetting(TunableFloatSettingT[Tunable]): ...
class TunableFloatDescriptor(TunableDescriptorT[float,Tunable]):
    SETTING_CLASS = FloatSetting

def tunableFloat(  default:float,
        **kwds:Unpack[TUNABLE_SETTING_KWDS[float,TUNABLE_SELF_T]]
    ) -> Callable[
        [   Callable[[TUNABLE_SELF_T, FloatSetting, EvaluationContext],
             None]],
        TunableFloatDescriptor]:
    return tunableProperty( default, TunableFloatDescriptor, **kwds) # type: ignore


#############################################################################

class TunableSecondsSetting(TunableSettingT[TimeSpanInSeconds,TUNABLE_SELF_T]):
    TUNABLE_DEFAULTS:ClassVar[StrAnyDict] = {'kind': TimeSpanInSeconds, 'kindMatch': TimeSpanInSeconds}

TunableSecondsSettingT = GenericT(TunableSecondsSetting)
class SecondsSetting(TunableSecondsSettingT[Tunable]): ...
class TunableSecondsDescriptor(TunableDescriptorT[TimeSpanInSeconds,Tunable]):
    SETTING_CLASS = SecondsSetting

def tunableSeconds(  default:TimeSpanInSeconds,
        **kwds:Unpack[TUNABLE_SETTING_KWDS[TimeSpanInSeconds,TUNABLE_SELF_T]]
    ) -> Callable[
        [   Callable[[TUNABLE_SELF_T, SecondsSetting, EvaluationContext],
             None]],
        TunableSecondsDescriptor]:
    return tunableProperty( default, TunableSecondsDescriptor, **kwds) # type: ignore

#############################################################################

class TunableMillimetersSetting(TunableSettingT[Millimeters,TUNABLE_SELF_T]):
    TUNABLE_DEFAULTS:ClassVar[StrAnyDict] = {'kind': Millimeters, 'kindMatch': Millimeters}

TunableMillimetersSettingT = GenericT(TunableMillimetersSetting)
class MillimetersSetting(TunableMillimetersSettingT[Tunable]): ...
class TunableMillimetersDescriptor(TunableDescriptorT[Millimeters,Tunable]):
    SETTING_CLASS = MillimetersSetting

def tunableMillimeters(  default:Millimeters,
        **kwds:Unpack[TUNABLE_SETTING_KWDS[Millimeters,TUNABLE_SELF_T]]
    ) -> Callable[
        [   Callable[[TUNABLE_SELF_T, MillimetersSetting, EvaluationContext],
             None]],
        TunableMillimetersDescriptor]:
    return tunableProperty( default, TunableMillimetersDescriptor, **kwds) # type: ignore


#############################################################################

class TunableDegreesSetting(TunableSettingT[Degrees,TUNABLE_SELF_T]):
    TUNABLE_DEFAULTS:ClassVar[StrAnyDict] = {'kind': Degrees, 'kindMatch': Degrees}

TunableDegreesSettingT = GenericT(TunableDegreesSetting)
class DegreesSetting(TunableDegreesSettingT[Tunable]): ...
class TunableDegreesDescriptor(TunableDescriptorT[Degrees,Tunable]):
    SETTING_CLASS = DegreesSetting

def tunableDegrees(  default:Degrees,
        **kwds:Unpack[TUNABLE_SETTING_KWDS[Degrees,TUNABLE_SELF_T]]
    ) -> Callable[
        [   Callable[[TUNABLE_SELF_T, DegreesSetting, EvaluationContext],
             None]],
        TunableDegreesDescriptor]:
    return tunableProperty( default, TunableDegreesDescriptor, **kwds) # type: ignore

#############################################################################
__profileImport.complete(globals())
    
__all__ = [
            'Tunable', 'TunableSetting', 'TunableSettingT',
            'TunableDescriptor','TunableDescriptorT',
            'tunableFloat','TunableFloatSetting', 'TunableFloatSettingT','TunableFloatSetting','FloatSetting',
            'tunableBool', 'TunableBoolSetting', 'TunableBoolSettingT', 'TunableBoolSetting', 'BoolSetting',
            'tunableInt', 'TunableIntSetting', 'TunableIntSettingT', 'TunableIntSetting', 'IntSetting',
            'tunableZeroToOne', 'TunableZeroToOneDescriptor', 'TunableZeroToOneSetting', 'ZeroToOneSetting',
            'tunablePlusMinusOne', 'tunablePlusMinusOneT',  'TunablePlusMinusOneSetting','PlusMinusOneSetting',
            'tunableDegrees', 'TunableDegreesDescriptor', 'TunableDegreesSetting', 'DegreesSetting',
            'tunableMillimeters', 'TunableMillimetersDescriptor', 'TunableMillimetersSetting', 'MillimetersSetting',
            'tunableSeconds', 'TunableSecondsDescriptor', 'TunableSecondsSetting', 'SecondsSetting',

           ]
