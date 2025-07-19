"""grouped import for common CircuitPython Wifi / http specific modules

Intended to be uses as `from LumensalisCP.commonCPWifi import *`

Partly for convenience and DRY, but also to minimize missing import problem reports
"""



from .commonCP import *
import adafruit_httpserver # type: ignore
import socketpool
import wifi,  mdns