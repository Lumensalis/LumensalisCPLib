
import LumensalisCP.Main
from LumensalisCP.CPTyping import TYPE_CHECKING
from LumensalisCP.Main.Expressions import TERM, NOT, CallbackSource, Expression, MAX, MIN
from LumensalisCP.Main.Expressions import rising, falling


MILLIS = CallbackSource( "MILLIS", lambda: LumensalisCP.Main.MainManager.theManager.millis ) # type: ignore # pylint: disable=no-member
CYCLES = CallbackSource( "CYCLES", lambda: LumensalisCP.Main.MainManager.theManager.cycle ) # type: ignore # pylint: disable=no-member
