from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__profileImport = getImportProfiler( globals() ) # "Outputs"

# pyright: reportUnusedImport=false

from LumensalisCP.Eval.Expressions import *
from LumensalisCP.Outputs import NamedNotifyingOutputTarget, NotifyingOutputTargetT,OutputTarget
from LumensalisCP.Interactable import Interactable, InteractableT, INTERACTABLE_ARG_T, INTERACTABLE_T, INTERACTABLE_ARG_T_KWDST

#############################################################################

__profileImport.parsing()
if TYPE_CHECKING:
   from LumensalisCP.Tunable import TunableSettingT, TunableSetting, Tunable
   
#############################################################################
TUNABLE_ARG_T=TypeVar('TUNABLE_ARG_T')
TUNABLE_T=TypeVar('TUNABLE_T')
TUNABLE_SELF_T=TypeVar('TUNABLE_SELF_T', bound='Tunable')


#############################################################################

class TUNABLE_SETTING_KWDS(INTERACTABLE_ARG_T_KWDST[TUNABLE_ARG_T, TUNABLE_T], 
                           NamedNotifyingOutputTarget.KWDS,
                           Generic[TUNABLE_ARG_T, TUNABLE_T,TUNABLE_SELF_T]
                    ):
    onChange: NotRequired[
         Callable[[TUNABLE_SELF_T, TunableSetting[TUNABLE_ARG_T, TUNABLE_T,TUNABLE_SELF_T], EvaluationContext], None] ]

TUNABLE_SETTING_KWDS_T = GenericT(TUNABLE_SETTING_KWDS)

##########################
#############################################################################

__profileImport.complete(globals())
    
__all__ = [
            'TUNABLE_SETTING_KWDS', 'TUNABLE_SETTING_KWDS_T', 'TUNABLE_ARG_T', 'TUNABLE_T', 'TUNABLE_SELF_T',

           ]
