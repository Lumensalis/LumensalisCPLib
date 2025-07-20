"""grouped import for common CircuitPython specific modules

Intended to be uses as `from LumensalisCP.commonCP import *`

Partly for convenience and DRY, but also to minimize missing import problem reports
"""
import io
import gc, neopixel # pyright: ignore[reportMissingImports,reportMissingModuleSource] # pylint: disable=import-error
import digitalio, analogio, pwmio, busio
import supervisor, board, microcontroller
