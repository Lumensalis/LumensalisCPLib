from __future__ import annotations

from LumensalisCP.ImportProfiler import getReloadableImportProfiler
__sayHTTPControlVarsRLImport = getReloadableImportProfiler( __name__, globals() )

#############################################################################
# pyright: reportPrivateUsage=false, reportUnusedImport=false

from LumensalisCP.HTTP.BSR.common import *
from LumensalisCP.Main.Panel import PanelControl, PanelMonitor
from LumensalisCP.util.ObjToDict import objectToDict
from LumensalisCP.Eval.Evaluatable import NamedEvaluatableProtocolT, NamedEvaluatableProtocol

from LumensalisCP.HTTP.BSR import UIPanelHelpersRL, UIPageHelpersRL

#############################################################################

_module = ReloadableModule( 'LumensalisCP.HTTP.BasicServer' )
_BasicServer = _module.reloadableClassMeta('BasicServer')

# pyright: reportPrivateUsage=false

@_BasicServer.reloadableMethod()
def BSR_client(self:BasicServer, request: Request):

    monitored = [mv.source for mv in self.main.panel.monitored.values()]
    print( f"get /client with {[(v.name,type(v)) for v in monitored]}")
    gc.collect()
    print( "BSR CLIENT **************************************************" )
    page = UIPageHelpersRL.UIPage(self.main)
    for panel in self.main.controlPanels:
        parts = UIPanelHelpersRL.PanelParts(page,panel)
    

    html = page.makeHtml()
    
    return Response(request, html, content_type="text/html")

    
__sayHTTPControlVarsRLImport.complete(globals())
