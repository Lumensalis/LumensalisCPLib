
from __future__ import annotations

from LumensalisCP.ImportProfiler import getReloadableImportProfiler
__profileImport = getReloadableImportProfiler( __name__, globals() )

#############################################################################
# pyright: reportPrivateUsage=false, reportUnusedImport=false

from LumensalisCP.HTTP.BSR.common import *

#############################################################################

def serveHomePage(self:BasicServer, request: Request) -> Response:
    self.infoOut( "base request...")
    with open("/www/index.html","r") as f:
        html = f.read()
        return Response(request, html, content_type="text/html")


__profileImport.complete(globals())