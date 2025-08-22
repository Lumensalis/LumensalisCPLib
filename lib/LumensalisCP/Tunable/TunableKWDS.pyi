from __future__ import annotations
from lib2to3.fixes.fix_idioms import TYPE


# pyright: reportUnusedImport=false

from LumensalisCP.Eval.Expressions import *
from LumensalisCP.Outputs import NamedNotifyingOutputTarget, NotifyingOutputTargetT,OutputTarget
from LumensalisCP.Interactable.Interactable import Interactable, InteractableT, INTERACTABLE_ARG_T, INTERACTABLE_T, INTERACTABLE_KWDS

#############################################################################
if TYPE_CHECKING:
    from LumensalisCP.Tunable.Tunable import TunableSettingT, TunableSetting, Tunable, TUNABLE_SELF_T

#############################################################################
TUNABLE_ARG_T=TypeVar('TUNABLE_ARG_T')
TUNABLE_T=TypeVar('TUNABLE_T')


#############################################################################

class TUNABLE_SETTING_KWDS[TUNABLE_T,TUNABLE_SELF_T](INTERACTABLE_KWDS[TUNABLE_T], 
                           NamedNotifyingOutputTarget.KWDS,
                    ):
    onChange: NotRequired[
         Callable[[TUNABLE_SELF_T, TunableSetting[ TUNABLE_T,TUNABLE_SELF_T], EvaluationContext], None] ]

TUNABLE_SETTING_KWDS_T = GenericT(TUNABLE_SETTING_KWDS)


__all__ = [
            'TUNABLE_SETTING_KWDS', 'TUNABLE_SETTING_KWDS_T', 'TUNABLE_ARG_T', 'TUNABLE_T' 

           ]
