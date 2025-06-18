from .Expressions import TERM, NOT, CallbackSource, Expression
from .Expressions import rising, falling
from .Manager import MainManager
MILLIS = CallbackSource( "MILLIS", lambda: MainManager.theManager.millis )
CYCLES = CallbackSource( "CYCLES", lambda: MainManager.theManager.cycle )

