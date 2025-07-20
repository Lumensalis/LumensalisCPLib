
import LumensalisCP.Main
from LumensalisCP.CPTyping import TYPE_CHECKING
from LumensalisCP.Eval.Expressions import TERM, NOT, CallbackSource, Expression, MAX, MIN
from LumensalisCP.Eval.Expressions import rising, falling

# TODO: directly access theManager
MILLIS = CallbackSource( "MILLIS", lambda: LumensalisCP.Main.MainManager.theManager.millis ) # type: ignore # pylint: disable=no-member
CYCLES = CallbackSource( "CYCLES", lambda: LumensalisCP.Main.MainManager.theManager.cycle ) # type: ignore # pylint: disable=no-member
