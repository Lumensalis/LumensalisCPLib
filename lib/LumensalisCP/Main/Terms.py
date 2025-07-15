from .Expressions import TERM, NOT, CallbackSource, Expression, MAX, MIN
from .Expressions import rising, falling

import LumensalisCP.Main
MILLIS = CallbackSource( "MILLIS", lambda: LumensalisCP.Main.MainManager.theManager.millis )
CYCLES = CallbackSource( "CYCLES", lambda: LumensalisCP.Main.MainManager.theManager.cycle )

