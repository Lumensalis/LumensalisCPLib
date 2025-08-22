from __future__ import annotations

# pylint: disable=redefined-builtin,unused-variable,unused-argument,broad-exception-caught
# pyright: reportUnusedImport=false

from LumensalisCP.IOContext import *


#############################################################################

INTERACTABLE_ARG_T = TypeVar('INTERACTABLE_ARG_T')
INTERACTABLE_T = TypeVar('INTERACTABLE_T')

class INTERACTABLE_ARG_T_ADD_KWDS[INTERACTABLE_ARG_T](TypedDict):
    startingValue: NotRequired[INTERACTABLE_ARG_T]
    min: NotRequired[INTERACTABLE_ARG_T]
    max: NotRequired[INTERACTABLE_ARG_T]
    name: NotRequired[str]
    description: NotRequired[str]
    
class INTERACTABLE_KWDS[INTERACTABLE_ARG_T](TypedDict):
    startingValue: NotRequired[INTERACTABLE_ARG_T]
    min: NotRequired[INTERACTABLE_ARG_T]
    max: NotRequired[INTERACTABLE_ARG_T]
    name: NotRequired[str]
    description: NotRequired[str]
    kindMatch: NotRequired[type]
    kind: NotRequired[str|type]

#############################################################################

 
#############################################################################
__all__ = [
    "INTERACTABLE_ARG_T",
    "INTERACTABLE_T",
    "INTERACTABLE_ARG_T_ADD_KWDS",
    "INTERACTABLE_KWDS"
]
