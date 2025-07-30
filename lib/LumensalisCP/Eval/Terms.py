# pyright: reportUnusedImport=false, reportImportCycles=false, reportMissingImports=false
# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false,  reportUnknownVariableType=false

from LumensalisCP.Main.PreMainConfig import pmc_getImportProfiler
_sayEvalTermsImport = pmc_getImportProfiler( "Eval.Terms" )

import LumensalisCP.Main
from LumensalisCP.CPTyping import TYPE_CHECKING
from LumensalisCP.Eval.ExpressionTerm import TERM, NOT, CallbackSource, MAX, MIN
from LumensalisCP.Eval.ExpressionTerm import rising, falling
from LumensalisCP.Eval.Expressions import Expression

# TODO: directly access theManager
MILLIS = CallbackSource( "MILLIS", lambda: LumensalisCP.Main.MainManager.theManager.millis ) # type: ignore # pylint: disable=no-member
CYCLES = CallbackSource( "CYCLES", lambda: LumensalisCP.Main.MainManager.theManager.cycle ) # type: ignore # pylint: disable=no-member

_sayEvalTermsImport.complete(globals())
