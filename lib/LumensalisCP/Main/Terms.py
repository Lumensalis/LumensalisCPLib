from .Expressions import TERM, NOT, CallbackSource, Expression, MAX, MIN
from .Expressions import rising, falling

MILLIS = CallbackSource( "MILLIS", lambda: MainManager.theManager.millis )
CYCLES = CallbackSource( "CYCLES", lambda: MainManager.theManager.cycle )

