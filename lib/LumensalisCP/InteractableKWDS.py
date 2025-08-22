from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__importProfile = getImportProfiler( __name__, globals() )

# pylint: disable=redefined-builtin,unused-variable,unused-argument,broad-exception-caught
# pyright: reportUnusedImport=false

from LumensalisCP.IOContext import *


__importProfile.parsing()

#############################################################################

INTERACTABLE_ARG_T = TypeVar('INTERACTABLE_ARG_T')
INTERACTABLE_T = TypeVar('INTERACTABLE_T')

class INTERACTABLE_ARG_T_ADD_KWDS(TypedDict, Generic[INTERACTABLE_ARG_T]):
    pass

class INTERACTABLE_KWDS(TypedDict):
    pass

#############################################################################

INTERACTABLE_KWDST = GenericT(INTERACTABLE_KWDS)


#############################################################################

 
#############################################################################
__all__ = [
    "INTERACTABLE_ARG_T",
    "INTERACTABLE_T",
    "INTERACTABLE_ARG_T_ADD_KWDS",
    "INTERACTABLE_KWDS",
]
__importProfile.complete()
