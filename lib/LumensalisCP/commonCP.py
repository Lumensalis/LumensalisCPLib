"""grouped import for common CircuitPython specific modules

Intended to be uses as `from LumensalisCP.commonCP import *`

Partly for convenience and DRY, but also to minimize missing import problem reports
"""

import digitalio, analogio, pwmio
import supervisor, board, microcontroller
import neopixel # pyright: ignore[reportMissingImports]
import io, gc