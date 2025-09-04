from __future__ import annotations

from LumensalisCP.ImportProfiler import getReloadableImportProfiler
__profileImport = getReloadableImportProfiler( __name__, globals() )

#############################################################################
# pyright: reportPrivateUsage=false, reportUnusedImport=false

from LumensalisCP.HTTP.BSR.common import *
from LumensalisCP.HTTP._httpBits import *
from LumensalisCP.util.Reloadable import addReloadableClass, reloadingMethod

if TYPE_CHECKING:
    from .BasicServer import BasicServer

#############################################################################

__profileImport.parsing()

class WebsocketSession(Debuggable):

    def __init__(self, server:BasicServer,request: Request) -> None:
        Debuggable.__init__(self)
        self.websocket:Websocket|None = Websocket(request, buffer_size=8192)
        self.priorMonitoredValue:dict[str, Any] = {}
        server.websockets.append(self)
        self.useStringIO = True
        self._ws_jsonBuffer:io.StringIO|None = io.StringIO(8192) if self.useStringIO else None # type:ignore[assignment]
        self.__server = weakref.ref(server)

    @property
    def server(self) -> BasicServer:
        server = self.__server()
        assert server is not None
        return server

    def connect(self):
        pass

    @reloadingMethod
    def updateSocketClient(self)->None:...

    @reloadingMethod
    def handle_websocket_request(self): ...

    @reloadingMethod
    def close(self): ...

addReloadableClass(WebsocketSession)

#############################################################################

__all__ = ["WebsocketSession"]

__profileImport.complete()
