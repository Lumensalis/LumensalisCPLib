from __future__ import annotations


from LumensalisCP.ImportProfiler import getReloadableImportProfiler
__sayHTTPControlVarsRLImport = getReloadableImportProfiler( __name__, globals() )

#############################################################################
# pyright: reportPrivateUsage=false, reportUnusedImport=false

from LumensalisCP.HTTP.BSR.common import *
from LumensalisCP.Main.Panel import PanelControl, PanelMonitor
from LumensalisCP.util.ObjToDict import objectToDict
from LumensalisCP.Eval.Evaluatable import NamedEvaluatableProtocolT, NamedEvaluatableProtocol
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
    parts = PanelParts(self.main)

    for v in self.main.panel.controls.values():
        print( f"  adding control {v.name} ({type(v)}) {v.kindMatch} {v.kind}" )
        parts.addControl(v)

    for v in self.main.panel.monitored.values(): 
        print( f"  adding monitored {v.source.name} ({type(v)})")
        parts.addMonitored(v)

    parts.finish()

    html = parts.makeHtml()
    
    return Response(request, html, content_type="text/html")

class PanelControlInstanceHelper(CountedInstance):
    
    kindMatch:type|None
    input:NamedEvaluatableProtocol[Any]

    def __init__(self, panelInstance:PanelControl[Any,Any]|PanelMonitor[Any]):
        super().__init__()
        self.panelInstance = panelInstance
        if isinstance(panelInstance, PanelMonitor):
            self.input = panelInstance.source
            self.kindMatch = None
        else:
            assert isinstance(panelInstance, PanelControl), f"panelInstance must be a PanelControl or PanelMonitor, got {type(panelInstance)}"
            self.input = panelInstance

            assert self.panelInstance.kind is not None, f"panelInstance.kind is None for {self.panelInstance.name} ({type(self.panelInstance)})"
            assert self.panelInstance.kindMatch is not None, f"panelInstance.kind is None for {self.panelInstance.name} ({type(self.panelInstance)})"
            self.kindMatch = self.panelInstance.kindMatch
        
        self.nameId = self.input.name

        self.editable:bool = isinstance(panelInstance,PanelControl)

    
    def getCellContent(self,tag:str) -> Iterable[str]:
            panelInstance = self.panelInstance
            if tag == 'name':
                if isinstance(panelInstance, PanelMonitor):
                    yield panelInstance.source.name
                else:
                    yield panelInstance.name
            elif tag == 'description':
                description = getattr(panelInstance,'description',None ) # or f"{panelInstance.name} ({type(self).__name__})"
                yield description or ''
            elif tag == 'min':
                yield str(panelInstance._min)
            elif tag == 'value':
                yield self.valueCell()
            elif tag == 'edit':
                yield self.editCell()
            elif tag == 'max':
                yield str(panelInstance._max)
            elif tag == 'etc':
                yield repr(panelInstance.kind)
                #yield f"{repr(self.kindMatch)} / {id(panelInstance)} {panelInstance.dbgName} {repr(panelInstance.kind)}  / {repr(panelInstance.kindMatch)} / {type(self).__name__}"
            else:
                yield f"Unknown tag {tag} for {panelInstance.name} ({type(panelInstance)})"

    def valueCell(self)-> str:
        return f'<div id="{self.nameId}">-</div>'
    
    def editCell(self)-> str:
        return f'<input id="{self.nameId}_edit" type="text" value="-"/>'

    def jsSelectBlock(self):
        return f'''
                const {self.nameId}Selector = document.querySelector("#{self.nameId}");
                const {self.nameId}EditSelector = document.querySelector("#{self.nameId}_edit");
                '''

    def wsReceivedBlock(self) -> str:
        return   f"""
                        if( receivedMessage.{self.nameId} !== undefined ) {{
                            value = receivedMessage.{self.nameId};
                            console.log( "received {self.nameId} ", value );
                            {self.wsCellUpdate()}
                        }}
""" 

    def wsCellUpdate(self) -> str:
        return f'console.log( "..." );'
    
class BasicPanelControlInstanceHelper(PanelControlInstanceHelper):

    
    def wsCellUpdate(self) -> str:
        return f'{self.nameId}Selector.textContent = value;'

class EditCapablePanelControlInstanceHelper(PanelControlInstanceHelper):

    def jsSelectBlock(self):
        if not self.editable:
            return super().jsSelectBlock()
        return super().jsSelectBlock() + \
            f"""
            {self.nameId}EditSelector.oninput = ( debounce(() => {{
                const packet = JSON.stringify( 
                    {{ name: '{self.nameId}', value: {self.nameId}EditSelector.value }}
                    );
                console.log( "sending packet", packet );
                ws.send( packet );
                {self.nameId}Selector.textContent = {self.nameId}EditSelector.value;

            }},200 ) );
            """
    
    def valueCell(self)-> str:
        return f'<div id="{self.nameId}">{self.panelInstance.controlValue}</div>'

class IntPanelControlInstanceHelper(EditCapablePanelControlInstanceHelper):
    
    def editCell(self)-> str:
        low = self.panelInstance._min
        high = self.panelInstance._max
        assert isinstance(low, int)
        assert isinstance(high, int)
        span = high - low
        assert span > 0, f"span must be positive, got {span} for {self.panelInstance.name} ({type(self.panelInstance)})"
        assert isinstance( self.panelInstance, PanelControl)
        return f'<input id="{self.nameId}_edit" type="range" min="{low}" max="{high}" value="{self.panelInstance.controlValue}"/>'


    def wsCellUpdate(self):
        return f'{self.nameId}Selector.textContent = value;'

class BoolPanelControlInstanceHelper(EditCapablePanelControlInstanceHelper):
    
    def editCell(self)-> str:
        assert isinstance( self.panelInstance, PanelControl)
        return f'<input id="{self.nameId}_edit" type="checkbox" value="{self.panelInstance.controlValue}"/>'

    def wsCellUpdate(self):
        return f'{self.nameId}Selector.textContent = value;'

class FloatPanelControlInstanceHelper(EditCapablePanelControlInstanceHelper):

    def wsCellUpdate(self):
        return f'{self.nameId}Selector.textContent = value;'
    
    def editCell(self)-> str:
        low = self.panelInstance._min
        high = self.panelInstance._max
        assert isinstance(low, (int, float)), f"low for {self.nameId} must be int or float, got {type(low)}"
        assert isinstance(high, (int, float)), f"high for {self.nameId}must be int or float, got {type(high)}"
        span = high - low
        assert isinstance( self.panelInstance, PanelControl)
        return f'<input id="{self.nameId}_edit" type="range" min="{low}" max="{high}" value="{self.panelInstance.controlValue}" step="{span/100}"/>'


    
class RGBPanelControlInstanceHelper(EditCapablePanelControlInstanceHelper):

    def editCell(self): 
        return f'<input id="{self.nameId}_edit" type="color">'


class SimpleTable(CountedInstance):

    def __init__(self, title:str, headers:list[str]):
        super().__init__()
        self.title = title
        self.headers = headers
        self.rows:list[PanelControlInstanceHelper] = []

    def startTable(self) -> Iterable[str]:
        yield """
    
    <table class="center">
        <thead>
            <tr>
            """
        for h in self.headers:
            yield "<th>"
            yield h
            yield "</th>"
            
        yield """        
            </tr>
        </thead>
    <tbody>

    """
    def endTable(self) -> Iterable[str]:
        yield """
        </tbody>
    </table>
    
        """
    def addRow(self, row:PanelControlInstanceHelper ) -> None:
        self.rows.append(row)

    def htmlBlock(self) -> Iterable[str]: 
        yield from self.startTable()
        for row in self.rows:
            yield "<tr>"
            for tag in self.headers:
                yield "<td>"
                yield from row.getCellContent(tag)
                yield "</td>"
            yield "</tr>"
        yield from self.endTable()

    
class PanelParts(CountedInstance):
    def __init__(self, main:MainManager):
        super().__init__()
        self.main = main
        self.htmlParts:list[str] = []

        self.controlHtmlParts = SimpleTable( "Controls",
                ["name","description","min","value","max","edit","etc"]  )
        self.monitorHtmlParts = SimpleTable( "Monitor",["name","description","value"] )

        self.triggerHtmlParts:list[str] = []
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
            elif kind  in ( "float", "TimeSpanInSeconds" ):
                instanceHelper = FloatPanelControlInstanceHelper( input )
            elif kind  in ( "bool","switch" ):
                instanceHelper = BoolPanelControlInstanceHelper(input)

            else:
                kindMatch = control.kindMatch
                if kindMatch is RGB:
                    instanceHelper = RGBPanelControlInstanceHelper( input )
                elif kindMatch is float:
                    instanceHelper = FloatPanelControlInstanceHelper( input )
                elif kindMatch is bool:
                    instanceHelper = BoolPanelControlInstanceHelper(input)
                elif kindMatch is int:
                    instanceHelper = IntPanelControlInstanceHelper(input)

                else:
                    instanceHelper = BasicPanelControlInstanceHelper( input )

            self.controlHtmlParts.addRow( instanceHelper )
            
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

            self.monitorHtmlParts.addRow( instanceHelper )
            self.jsSelectors.append( instanceHelper.jsSelectBlock() )
            self.wsReceived.append( instanceHelper.wsReceivedBlock() )

    def finish(self):
        self.wsReceived.append( '''
                           
                    } catch (error) {
                        console.error('Error parsing JSON:', error);
                    }
                }
''' )

    def _yieldHtml(self) -> Iterable[str]:
        yield HTML_TEMPLATE_A

        for parts in (self.controlHtmlParts, self.monitorHtmlParts):
            yield "<h2>" + parts.title + "</h2>"
            yield from parts.htmlBlock()

        yield """ <p>  <p> <h2> Triggers </h2> """
        yield """ <span class="triggers"> <div class="triggers">"""
        for part in self.main.panel._triggers:
            triggerName = part.name
            yield f"""
<button type="button" id="{triggerName}_trigger">{triggerName}</button>
            """
            self.jsSelectors.append( f"""
            const {triggerName}TriggerSelector = document.querySelector("#{triggerName}_trigger");
            {triggerName}TriggerSelector.onclick = ( () => {{
                const packet = JSON.stringify( {{ trigger: '{triggerName}' }});
                console.log( "sending packet", packet );
                ws.send( packet );
            }} );
            """ )

        yield """</div></span>"""
        
        yield  HTML_TEMPLATE_B
        yield from self.jsSelectors
        yield from self.wsReceived
        yield HTML_TEMPLATE_Z

    def y2(self) -> Iterable[str]:
        prior:Any = None
        x = 0

        for s in self._yieldHtml():
            x +=1
            if s is None: # type: ignore
                yield "NONE"
                continue
            assert isinstance(s, str), f"cannot yield ({type(s)}) : {repr(s)} at {x}, prior={prior}"
            yield s
            prior = s

    def makeHtml(self) -> str:

        html =  "\n".join(self.y2())
        return html
    
        parts:list[str] = [HTML_TEMPLATE_A]

        
        parts.extend(self.htmlParts)
        parts.append( """
        </tbody>
    </table>
""" )

        parts.append( HTML_TEMPLATE_B )
        parts.extend(self.jsSelectors)
        parts.extend(self.wsReceived)
        parts.append( HTML_TEMPLATE_Z )
        return "\n".join(parts)

class PanelControlTemplateHelper(object):
    
    def __init__( self, main:MainManager ):
        self.main = main
    
    
    def varBlocks(self, vars:List[PanelMonitor[Any]]) -> PanelParts:
        parts = PanelParts(self.main)

        for v in vars: #self.main._controlVariables.values():
            parts.addMonitored(v)

        parts.finish()
        return parts

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
