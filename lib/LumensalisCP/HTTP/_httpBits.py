from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__sayImport = getImportProfiler( __name__, globals() ) 

# pyright: reportUnusedImport=false, reportUnusedVariable=false

import adafruit_httpserver # type: ignore
import wifi
import mdns
import supervisor
import gc
import microcontroller, board

from adafruit_httpserver.methods import POST, PUT, GET   # type: ignore # pylint: disable=import-error,no-name-in-module
from adafruit_httpserver import Server, Request, Response, Websocket, Route, JSONResponse  # pylint: disable=import-error,no-name-in-module # type: ignore


from LumensalisCP.commonCPWifi import *

__sayImport.complete(globals())