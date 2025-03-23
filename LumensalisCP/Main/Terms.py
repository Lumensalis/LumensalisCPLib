from .Expressions import TERM, NOT, CallbackSource, Expression

from .Manager import MainManager
MILLIS = CallbackSource( "MILLIS", lambda: MainManager.theManager.millis )
CYCLES = CallbackSource( "CYCLES", lambda: MainManager.theManager.cycle )