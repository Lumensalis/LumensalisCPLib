# SPDX-FileCopyrightText: 2023 Michał Pokusa
# SPDX-FileCopyrightText: 2025 James Fowler
#
# SPDX-License-Identifier: Unlicense
import LumensalisCP.Main.Manager
from LumensalisCP.common import *

from asyncio import create_task, gather, run, sleep as async_sleep
from LumensalisCP.Inputs import InputSource
from LumensalisCP.commonCPWifi import *
from adafruit_httpserver.methods import POST, PUT, GET   # pyright: ignore[reportMissingImports]
from adafruit_httpserver import Server, Request, Response, Websocket, Route, JSONResponse   # pyright: ignore[reportAttributeAccessIssue]

from .ControlVars import ControlValueTemplateHelper

from LumensalisCP.pyCp.importlib import reload
from . import BasicServerRL

from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl

class BasicServer(Server,Debuggable):
    
    def __init__( self, *args, main:"LumensalisCP.Main.Manager.MainManager"=None, **kwds ):
        
        assert main is not None
        
        self.pool = main.socketPool
        Server.__init__(self, self.pool, debug=pmc_mainLoopControl.enableHttpDebug )
        Debuggable.__init__(self)

        # TODO: make actual client instance for multiple connections...???
        self.websocket: Websocket = None
        self.cvHelper = ControlValueTemplateHelper( main=main )

        self.main = main
        self.monitoredVariables:List[InputSource] = []
        self.priorMonitoredValue = {}
        self._setupRoutes()
        
        TTCP_HOSTNAME = main.config.options.get('TTCP_HOSTNAME',None)
        #print(f"BasicServer TTCP_HOSTNAME = {TTCP_HOSTNAME}")
        #if (TTCP_HOSTNAME := main.config.options.get('TTCP_HOSTNAME',None)) is not None:
        if TTCP_HOSTNAME is not None:
            self.infoOut(f"setting HOSTNAME to {TTCP_HOSTNAME}")
            self.mdns_server = mdns.Server(wifi.radio)
            #self.mdns_server.hostname = TTCP_HOSTNAME
            self.mdns_server.instance_name = TTCP_HOSTNAME
            self.mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=5000)
        
    def __str__(self):
        port = f":{self.port}"
        url = f"http://{self.host}{port}"
        return f"{self.__class__.__name__}( {url} addr={wifi.radio.ipv4_address} )"
    
    def monitorControlVariable( self, v:InputSource ):
        # TODO: handle additions after server startup better
        self.monitoredVariables.append(v)

    def monitorInput( self, v:InputSource ):
        # TODO: handle additions after server startup better
        self.monitoredVariables.append(v)

    HTML_TEMPLATE_A = """
<html lang="en">
    <head>
        <title>Websocket Client</title>
    </head>
    <body>
"""

    HTML_TEMPLATE_B = """
        <script>
            console.log('client on ' + location.host );

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

    def addReloadableRouteHandler( self, name, methods=[GET,POST,PUT], params:Optional[str]=None ):
        functionName = f'BSR_{name}'
        
        def handler(request: Request,reloading=False,**kwds):
            try:
                c = getattr( BasicServerRL, functionName, None )
                ensure( c is not None, "missing reloadable %r", functionName )
                self.enableDbgOut and self.dbgOut( f"handling reloadable route {name} with {functionName}, reloading={reloading} params={params}, kwds={kwds}")
                rv =c(self,request,**kwds)
                if rv is not None: return rv
                return JSONResponse(request, {"unhandled request": name } )
            except Exception as inst:
                return BasicServerRL.ExceptionResponse(request, inst, "route exception" )

        def reloadingHandler(request: Request,**kwds):
            if supervisor.runtime.autoreload:
                self.infoOut( "/%s request disabling autoreload", name )
                supervisor.runtime.autoreload = False
            self.infoOut( "reloading BasicServerRL" )
            reload( BasicServerRL )
            return handler(request,reloading=True,**kwds)
        
        if params is not None:
            self.add_routes( [
                Route(f'/{name}Reload/{params}', methods, reloadingHandler),
                Route(f'/{name}/{params}', methods, handler),
            ] )
        else:
            self.add_routes( [
                Route(f'/{name}Reload', methods, reloadingHandler, append_slash=True),
                Route(f'/{name}Reload/...', methods, reloadingHandler, append_slash=True),
                Route(f'/{name}', methods, handler, append_slash=True),
                Route(f'/{name}/...', methods, handler, append_slash=True),
            ] )
        
    def _setupRoutes(self):
        # print( "_setupRoutes" )

        self.addReloadableRouteHandler( "client", [GET])
        self.addReloadableRouteHandler( "sak" )
        self.addReloadableRouteHandler( "query", params="<name>" )
        self.addReloadableRouteHandler( "cmd", [PUT,POST], params="<cmd>"  )

        @self.route("/connect-websocket", GET)
        def connect_client(request: Request):
            #global websocket  # pylint: disable=global-statement

            if self.websocket is not None:
                
                self.websocket.close()  # Close any existing connection
                

            self.websocket = Websocket(request)
            self.priorMonitoredValue = {}
            return self.websocket
        
        @self.route("/")
        def base(request: Request):
            """
            Serve a default static plain text message.
            """
            self.infoOut( "base request...")
            return Response(request, "Hello from the CircuitPython HTTP Server!")
        
    async def handle_http_requests(self):
        try:
            
            while True:
                #print( "handle_http_requests poll..")
                pool_result = self.poll()
                if pool_result == adafruit_httpserver.REQUEST_HANDLED_RESPONSE_SENT:
                    # Do something only after handling a request
                    self.infoOut( "handle_http_requests handled request")
                    pass
                
                #print( "handle_http_requests sleep..")
                await async_sleep(0.05)
    
        except Exception  as error:
            self.SHOW_EXCEPTION( error, 'handle_http_requests error' )
            

    async def handle_websocket_requests(self):
        try:
            self.startupOut( 'handle_websocket_requests starting' )

            while True:
                if self.websocket is not None:
                    if (data := self.websocket.receive(fail_silently=True)) is not None:
                        
                        try:
                            # print( f'websocket data = {data}' )
                            jdata = json.loads(data)
                            self.main.handleWsChanges(jdata)
                        except Exception as inst:
                            self.SHOW_EXCEPTION( inst, "error on incoming websocket data %r", data )

                await async_sleep(0.05)
        except Exception  as error:
            self.SHOW_EXCEPTION( error, 'handle_websocket_requests error' )


    async def send_websocket_messages(self):
        
        try:
            useStringIO = False
            jsonBuffer = io.StringIO(8192) if useStringIO else None
            while True:
                if self.websocket is not None:
                    payload = {}
                    for v in self.monitoredVariables:
                        currentValue = v.getValue()
                        assert currentValue is not None
                        if currentValue != self.priorMonitoredValue.get(v.name,None):
                            payload[v.name] = currentValue
                            self.priorMonitoredValue[v.name] = currentValue
                    if len(payload):
                        if useStringIO:
                            jsonBuffer.seek(0)
                            jsonBuffer.truncate()
                            json.dump( payload, jsonBuffer )
                        message = jsonBuffer.getvalue() if useStringIO else json.dumps(payload)
                        self.websocket.send_message(message, fail_silently=True)
                        self.enableDbgOut and self.dbgOut( "wrote WS update : %r", message )
                await async_sleep(0.5)
        except Exception  as error:
            SHOW_EXCEPTION( error, 'send_websocket_messages error' )

    def createAsyncTasks( self ):
        self.dbgOut( "createAsyncTasks... " )

        return [
            create_task(self.handle_http_requests()),
            create_task(self.handle_websocket_requests()),
            create_task(self.send_websocket_messages()),
        ]

