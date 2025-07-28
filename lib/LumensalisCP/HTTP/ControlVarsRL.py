from __future__ import annotations


from LumensalisCP.Main.PreMainConfig import ReloadableImportProfiler
__sayHTTPControlVarsRLImport = ReloadableImportProfiler( "HTTP.ControlVarsRL" )

from adafruit_httpserver import DELETE, GET, POST, PUT, JSONResponse, Request, Response  # pyright: ignore

from LumensalisCP.IOContext import *
from LumensalisCP.commonCPWifi import *
from LumensalisCP.HTTP import BasicServer
from LumensalisCP.Main.Panel import PanelControl, PanelMonitor


from LumensalisCP.CPTyping import *
from LumensalisCP.Inputs import InputSource


class PanelControlInstanceHelper(object):
    
    def __init__(self, panelInstance:PanelControl[Any,Any]|PanelMonitor[Any]):
        self.panelInstance = panelInstance
        if isinstance(panelInstance, PanelMonitor):
            self.input:InputSource  = panelInstance.source
        else:
            assert isinstance(panelInstance, PanelControl), f"panelInstance must be a PanelControl or PanelMonitor, got {type(panelInstance)}"
            self.input:InputSource = panelInstance
        
        self.nameId = self.input.name

        self.editable:bool = isinstance(panelInstance,PanelControl)

    def htmlBlock(self): 
        description = getattr(self.panelInstance,'description',None ) or f"{self.panelInstance.name} ({type(self.panelInstance).__name__})"
        return f'''
    <tr>
        <td>{self.panelInstance.name}</td>
        <td>{description}</td>
        <td>{self.panelInstance._min}</td>
        <td>{self.editCell() if self.editable else self.valueCell()}</td>
        <td>{self.panelInstance._max}</td>
    </tr>
        '''
    def valueCell(self)-> str:
        return f'<div id="{self.nameId}">-</div>'
    
    def editCell(self)-> str:
        return f'<input id="{self.nameId}_edit" type="text" value="-"/>'

    def jsSelectBlock(self):
        return f'''
                const {self.nameId}Selector = document.querySelector("#{self.nameId}");
                '''

    def wsReceivedBlock(self) -> str:
        return   f"""
                        if( receivedMessage.{self.nameId} !== undefined ) {{
                            value = receivedMessage.{self.nameId};
                            {self.wsCellUpdate()}
                        }}
""" 

    def wsCellUpdate(self) -> str:
        return f'console.log( "..." );'
    
class BasicPanelControlInstanceHelper(PanelControlInstanceHelper):
    
    def oldhtmlBlock(self): 
        description = getattr(self.panelInstance,'description',None ) or f"{self.panelInstance.name} ({type(self.panelInstance).__name__})"
        return f'<span>{description}: <div id="{self.panelInstance.name}">-</div></span>'
    
    #def valueCell(self)-> str:
    #    return f'<div id="{self.cv.name}">-</div>'
    
    def wsCellUpdate(self) -> str:
        return f'{self.nameId}Selector.textContent = value;'

class IntPanelControlInstanceHelper(PanelControlInstanceHelper):
    
    #def htmlBlock(self) -> str: 
    #    return f'<span>{self.cv.description}: <div id="{self.cv.name}">-</div></span>'
    
    def wsCellUpdate(self):
        return f'{self.nameId}Selector.textContent = value;'


class RGBPanelControlInstanceHelper(PanelControlInstanceHelper):

    def editCell(self): 
        return f'<input id="{self.nameId}" type="color">'

    def jsSelectBlock(self):
        return super().jsSelectBlock() + \
            f"""
            {self.nameId}Selector.oninput = debounce(() => 
                ws.send( JSON.stringify( {{ name: '{self.nameId}', 
                    value: {self.nameId}.value
                }} ) ), 200);
            """

class PanelParts(object):
    def __init__(self, main:MainManager):
        self.main = main
        self.htmlParts:list[str] = []
        self.jsSelectors:list[str] = []
        self.wsReceived:list[str] = []
        self.wsReceived.append( '''
            function handleWSMessage( event ) {
                try {
                    const receivedMessage = JSON.parse(event.data);
''' )

    def addControl(self, control:PanelControl[Any,Any]):
            input = control
            instanceHelper = None
            kind = getattr(input,'kind',None)
            if kind == "int":
                instanceHelper = IntPanelControlInstanceHelper( input )
            elif kind == "RGB":
                instanceHelper = RGBPanelControlInstanceHelper( input )
            else:
                instanceHelper = BasicPanelControlInstanceHelper( input )

            self.htmlParts.append( instanceHelper.htmlBlock() )
            if instanceHelper.editable:
                self.jsSelectors.append( instanceHelper.jsSelectBlock() )
            else:
                self.wsReceived.append( instanceHelper.wsReceivedBlock() )

    def addMonitored(self, monitored:PanelMonitor[Any]):
            #input = monitored.source
            instanceHelper = None
            kind = getattr(monitored,'kind',None)
            if kind == "int":
                instanceHelper = IntPanelControlInstanceHelper( monitored )
            elif kind == "RGB":
                instanceHelper = RGBPanelControlInstanceHelper( monitored )
            else:
                instanceHelper = BasicPanelControlInstanceHelper( monitored )

            self.htmlParts.append( instanceHelper.htmlBlock() )
            self.jsSelectors.append( instanceHelper.jsSelectBlock() )
            self.wsReceived.append( instanceHelper.wsReceivedBlock() )

    def finish(self):
        self.wsReceived.append( '''
                           
                    } catch (error) {
                        console.error('Error parsing JSON:', error);
                    }
                }
''' )

    def makeHtml(self) -> str:
        parts:list[str] = [HTML_TEMPLATE_A]
        parts.extend(self.htmlParts)
        parts.append( HTML_TEMPLATE_B )
        parts.extend(self.jsSelectors)
        parts.extend(self.wsReceived)
        parts.append( HTML_TEMPLATE_Z )
        return "\n".join(parts)

class PanelControlTemplateHelper(object):
    
    def __init__( self, main:MainManager ):
        self.main = main
    
    
    def varBlocks(self, vars:List[InputSource]) -> PanelParts:
        parts = PanelParts(self.main)

        for v in vars: #self.main._controlVariables.values():
            parts.addMonitored(v)

        parts.finish()
        return parts

HTML_TEMPLATE_A = """
<html lang="en">
    <head>
        <title>Websocket Client</title>
    </head>

    <body>
    <button type="button" id="myButton">Send REST Request</button>
    <div id="responseContainer"></div>
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Min</th>
                <th>Value</th>
                <th>Max</th>
            </tr>
        </thead>
        <tbody>
"""

HTML_TEMPLATE_B = """
        </tbody>
    </table>
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

def BSR_client(self:BasicServer.BasicServer, request: Request):

    monitored = [mv.source for mv in self.main.panel.monitored.values()]
    print( f"get /client with {[(v.name,type(v)) for v in monitored]}")
    #if self.cvHelper is None:
    #    self.cvHelper = PanelControlTemplateHelper( main=self.main )
    #assert isinstance(self.cvHelper, PanelControlTemplateHelper), "cvHelper is not a PanelControlTemplateHelper"

    # vb = self.cvHelper.varBlocks(monitored)
    parts = PanelParts(self.main)

    for v in self.main.panel.controls.values():
        print( f"  adding control {v.name} ({type(v)})")
        parts.addControl(v)

    for v in self.main.panel.monitored.values(): 
        print( f"  adding monitored {v.source.name} ({type(v)})")
        parts.addMonitored(v)

    parts.finish()
    

    html = parts.makeHtml()
    
    return Response(request, html, content_type="text/html")
    
__sayHTTPControlVarsRLImport.complete()
