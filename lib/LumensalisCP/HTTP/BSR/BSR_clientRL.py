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


HTML_TEMPLATE_Bggg = """
 
        <script>
            console.log('client on ' + location.host );

            document.getElementById('myButton').addEventListener('click', function() {
                fetch('/sakReload', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }) // Replace with your API endpoint
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json(); // Parse the response as JSON
                    })
                    .then(data => {
                        // Handle the JSON data received from the API
                        document.getElementById('responseContainer').innerHTML = JSON.stringify(data, null, 2);
                    })
                    .catch(error => {
                        console.error('There was a problem with the fetch operation:', error);
                        document.getElementById('responseContainer').innerHTML = 'Error: ' + error.message;
                    });
            });
            let ws = new WebSocket('ws://' + location.host + '/connect-websocket');
            ws.onopen = () => console.log('WebSocket connection opened');
            ws.onclose = () => console.log('WebSocket connection closed');
"""

    
__sayHTTPControlVarsRLImport.complete(globals())
