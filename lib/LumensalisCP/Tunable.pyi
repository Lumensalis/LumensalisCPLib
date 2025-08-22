from __future__ import annotations

# pyright: reportUnusedImport=false, reportPrivateUsage=false

from LumensalisCP.Eval.Expressions import *
from LumensalisCP.Outputs import NamedNotifyingOutputTarget, NotifyingOutputTargetT,OutputTarget
from LumensalisCP.Interactable import Interactable, InteractableT, INTERACTABLE_ARG_T, INTERACTABLE_T
from typing  import TypeVar, Generic, Callable, Any, Optional, Unpack, TypeAlias
from LumensalisCP.TunableKWDS import *
#############################################################################



#############################################################################
#TUNABLE_SELF_T=TypeVar('TUNABLE_SELF_T', bound='Tunable')
TUNABLE_SELF_T  = TypeVar('TUNABLE_SELF_T', bound='Tunable')

class TunableSetting[ TUNABLE_T,TUNABLE_SELF_T](NamedLocalIdentifiable,OutputTarget,
                     InteractableT[TUNABLE_T],
                     EvaluatableT[TUNABLE_T]):

    def __init__(self, tunable:TUNABLE_SELF_T,
            **kwargs:Unpack[TUNABLE_SETTING_KWDS[TUNABLE_T,TUNABLE_SELF_T]]
            ) -> None: ...
    
    def set( self, value:Any, context:EvaluationContext ) -> None: ...
    def settingUpdate( self, value:TUNABLE_T, 
                context:Optional[EvaluationContext]=None ) -> None: ...
    @property
    def value(self) -> TUNABLE_T: ...
    
    def __call__(self, context:Optional[EvaluationContext]=None) -> TUNABLE_T: ...
    
TunableSettingT = GenericT(TunableSetting)


#############################################################################
class TunableDescriptor[TUNABLE_T,TUNABLE_SELF_T]():
    def __init__(self, settingClass:type, 
                 **settingKwds:Unpack[TUNABLE_SETTING_KWDS[TUNABLE_T,TUNABLE_SELF_T]] 
                 ) -> None: ...

    def __makeSetting(self, instance:TUNABLE_SELF_T) -> TunableSetting[TUNABLE_T,TUNABLE_SELF_T]: ...
    def __getSetting(self, instance:TUNABLE_SELF_T) -> TunableSetting[TUNABLE_T,TUNABLE_SELF_T]: ...

    def __get__(self, instance:TUNABLE_SELF_T, owner:Any=None) -> TunableSetting[TUNABLE_T,TUNABLE_SELF_T]: ...
    def __set__(self, instance:TUNABLE_SELF_T, value:TUNABLE_T) -> None: ...
        
TunableDescriptorT = GenericT(TunableDescriptor)
#############################################################################

class Tunable(NliInterface):
    
    def __init__(self) -> None: ...
    def onSettingUpdate( self, setting:TunableSetting[TUNABLE_T,Self]) -> None: ...

        

#############################################################################


def tunableProperty[TUNABLE_T,TUNABLE_SELF_T, TUNABLE_DESCRIPTOR_T](  default:TUNABLE_T, 
        descriptorClass:TUNABLE_DESCRIPTOR_T,
        **kwds:Unpack[TUNABLE_SETTING_KWDS[TUNABLE_T,TUNABLE_SELF_T]]
    ) -> Callable[ 
            [Callable[[TUNABLE_SELF_T,TunableSetting[TUNABLE_T,TUNABLE_SELF_T],EvaluationContext],
                         None]],
                  TUNABLE_DESCRIPTOR_T]: ...


def tunablePropertyT[TUNABLE_T,TUNABLE_SELF_T, TUNABLE_DESCRIPTOR_T](  default:TUNABLE_T, 
        descriptorClass:TUNABLE_DESCRIPTOR_T,
        **kwds:Unpack[TUNABLE_SETTING_KWDS[TUNABLE_T,TUNABLE_SELF_T]]
    ) -> Callable[ 
            [Callable[[TUNABLE_SELF_T,TunableSetting[TUNABLE_T,TUNABLE_SELF_T],EvaluationContext],
                         None]],
                  TUNABLE_DESCRIPTOR_T]: ...

#############################################################################
__all__ = [
            'Tunable', 'TunableSetting', 'TunableSettingT',
            'TunableDescriptor','TunableDescriptorT',
            'TUNABLE_SELF_T',
            'tunableProperty', 'tunablePropertyT'

           ]
