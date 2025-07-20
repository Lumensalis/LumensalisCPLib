from LumensalisCP.CPTyping import TYPE_CHECKING

from .Expressions import TERM, NOT, CallbackSource, Expression, MAX, MIN
from .Expressions import rising, falling

import LumensalisCP
if TYPE_CHECKING:
    import LumensalisCP.Main
    import LumensalisCP.Main.Manager
    
MILLIS = CallbackSource( "MILLIS", lambda: LumensalisCP.Main.MainManager.theManager.millis ) # type: ignore
CYCLES = CallbackSource( "CYCLES", lambda: LumensalisCP.Main.MainManager.theManager.cycle ) # type: ignore

