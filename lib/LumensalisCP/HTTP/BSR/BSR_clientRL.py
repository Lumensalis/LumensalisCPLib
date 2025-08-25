from __future__ import annotations

from LumensalisCP.ImportProfiler import getReloadableImportProfiler
__sayHTTPControlVarsRLImport = getReloadableImportProfiler( __name__, globals() )

#############################################################################
# pyright: reportPrivateUsage=false, reportUnusedImport=false

from LumensalisCP.HTTP.BSR.common import *
from LumensalisCP.Main.Panel import PanelControl, PanelMonitor
from LumensalisCP.util.ObjToDict import objectToDict
from LumensalisCP.Eval.Evaluatable import NamedEvaluatableProtocolT, NamedEvaluatableProtocol

from LumensalisCP.HTTP.BSR import UIHelpers
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
    parts = UIHelpers.PanelParts(self.main)

    for v in self.main.panel.controls.values():
        print( f"  adding control {v.name} ({type(v)}) {v.kindMatch} {v.kind}" )
        parts.addControl(v)

    for v in self.main.panel.monitored.values(): 
        print( f"  adding monitored {v.source.name} ({type(v)})")
        parts.addMonitored(v)

    parts.finish()

    html = parts.makeHtml()
    
    return Response(request, html, content_type="text/html")


HTML_TEMPLATE_A = """
<html lang="en">
    <head>
        <title>Websocket Client</title>
        <style>
table, th, td {
  border: 1px solid black;
  border-radius: 10px;
padding: 15px;
}
h2 {
  text-align: center;
}
table.center {
  margin-left: auto;
  margin-right: auto;
}
.triggers {
  margin-left: auto;
  margin-right: auto;
  text-align: center;
}

</style>
    </head>

    <body>
    <button type="button" id="myButton">Send REST Request</button>
    <div id="responseContainer"></div>

"""

HTML_TEMPLATE_B = """
 
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
#            ws.onerror = error => cpuTemp.textContent = error;

HTML_TEMPLATE_Z = """            
            ws.onmessage = event => handleWSMessage( event );

            function debounce(callback, delay = 1000) {
                let timeout
                return (...args) => {
                    clearTimeout(timeout)
                    timeout = setTimeout(() => {
                    callback(...args)
                  }, delay)
                }
            }
            
        </script>
    </body>
</html>
"""
    
__sayHTTPControlVarsRLImport.complete(globals())
