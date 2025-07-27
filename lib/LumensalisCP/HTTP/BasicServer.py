# SPDX-FileCopyrightText: 2023 Michał Pokusa
# SPDX-FileCopyrightText: 2025 James Fowler
#
# SPDX-License-Identifier: Unlicense

from __future__ import annotations
from asyncio import create_task, sleep as async_sleep, Task

from adafruit_httpserver.methods import POST, PUT, GET   # type: ignore # pylint: disable=import-error,no-name-in-module
from adafruit_httpserver import Server, Request, Response, Websocket, Route, JSONResponse  # pylint: disable=import-error,no-name-in-module # type: ignore

from LumensalisCP.IOContext import *

from LumensalisCP.commonCPWifi import *


from LumensalisCP.pyCp.importlib import reload
from LumensalisCP.HTTP import BasicServerRL
from LumensalisCP.HTTP import ControlVarsRL


from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl

class BasicServer(Server,Debuggable):
    
    # type:ignore[unused-function]
    # type: ignore[reportUntypedFunctionDecorator,reportUnusedFunction]

    def __init__( self, main:MainManager ):
        
        assert main is not None
        
        self.pool = main.socketPool
        Server.__init__(self, self.pool, debug=pmc_mainLoopControl.enableHttpDebug )
        Debuggable.__init__(self)

        # TODO: make actual client instance for multiple connections...???
        self.websocket: Websocket|None = None
        self.cvHelper:ControlVarsRL.PanelControlTemplateHelper|None = ControlVarsRL.PanelControlTemplateHelper( main=main )

        self.main = main
        self.monitoredVariables:List[InputSource] = []
        self.priorMonitoredValue:dict[str,Any] = {}
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
        
    def __str__(self) -> str:
        port = f":{self.port}"
        url = f"http://{self.host}{port}"
        return f"{self.__class__.__name__}( {url} addr={wifi.radio.ipv4_address} )"
    
    def monitorControlVariable( self, v:InputSource ):
        # TODO: handle additions after server startup better
        self.monitoredVariables.append(v)

    def monitorInput( self, v:InputSource ):
        # TODO: handle additions after server startup better
        self.monitoredVariables.append(v)


    def addReloadableRouteHandler( self, name:str, 
                        methods:List[str]=[GET,POST,PUT], 
                        params:Optional[str]=None 
                    ) -> None:
        functionName = f'BSR_{name}'
        
        def handler(request: Request,reloading:bool=False,**kwds:StrAnyDict):
            try:
                c = getattr( BasicServerRL, functionName, None )
                if c is None:
                    c = getattr( ControlVarsRL, functionName, None )

                ensure( c is not None, "missing reloadable %r", functionName )
                if self.enableDbgOut: self.dbgOut( f"handling reloadable route {name} with {functionName}, reloading={reloading} params={params}, kwds={kwds}")
                rv =c(self,request,**kwds) # type:ignore[call-arg]
                if rv is not None: return rv
                return JSONResponse(request, {"unhandled request": name } )
            except Exception as inst:
                return BasicServerRL.ExceptionResponse(request, inst, "route exception" )

        def reloadingHandler(request: Request,**kwds:StrAnyDict):
            if supervisor.runtime.autoreload:
                self.infoOut( "/%s request disabling autoreload", name )
                supervisor.runtime.autoreload = False
            self.infoOut( "reloading BasicServerRL" )
            reload( ControlVarsRL )
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

        @self.route("/connect-websocket", GET) # type: ignore[reportUntypedFunctionDecorator,reportUnusedFunction]
        def connect_client(request: Request) -> Websocket: # pyright: ignore[reportUntypedFunctionDecorator,reportUnusedFunction]
            #global websocket  # pylint: disable=global-statement

            if self.websocket is not None:
                
                self.websocket.close()  # Close any existing connection
                

            self.websocket = Websocket(request, buffer_size=8192)
            self.priorMonitoredValue = {}
            return self.websocket
        
        @self.route("/") # type:ignore[override]
        def base(request: Request) -> Response: # type:ignore[reportUntypedFunctionDecorator,reportUnusedFunction]

            """
            Serve a default static plain text message.
            """
            self.infoOut( "base request...")
            return Response(request, "Hello from the CircuitPython HTTP Server!")
        
    async def handle_http_requests(self):
        try:
            
            while True:
                #print( "handle_http_requests poll..")
                try:
                    pool_result = self.poll()
                    if pool_result == adafruit_httpserver.REQUEST_HANDLED_RESPONSE_SENT:
                        # Do something only after handling a request
                        self.infoOut( "handle_http_requests handled request")
                        pass

                except Exception as error:
                    self.SHOW_EXCEPTION( error, 'handle_http_requests error' )
                    await async_sleep(0.25)
                #print( "handle_http_requests sleep..")
                await async_sleep(0.05)
    
        except Exception  as error:
            self.SHOW_EXCEPTION( error, 'handle_http_requests error' )
            

    async def handle_websocket_requests(self):
        try:
            self.startupOut( 'handle_websocket_requests starting' )

            while True:
                if self.websocket is not None:
                    BasicServerRL.handle_websocket_request(self)

                await async_sleep(0.05)
        except Exception  as error:
            self.SHOW_EXCEPTION( error, 'handle_websocket_requests error' )


    async def send_websocket_messages(self):
        
        try:
            useStringIO = False
            self._ws_jsonBuffer:io.StringIO|None = io.StringIO(8192) if useStringIO else None # type:ignore[assignment]
            while True:
                try:
                    BasicServerRL.updateSocketClient(self, useStringIO)
                except Exception as inst:
                    self.SHOW_EXCEPTION( inst, "error on sending websocket messages" )

                await async_sleep(0.5)
        except Exception  as error:
            SHOW_EXCEPTION( error, 'send_websocket_messages error' )

    def createAsyncTasks( self ) -> list[Task[None]]:
        self.dbgOut( "createAsyncTasks... " )

        return [
            create_task(self.handle_http_requests()),
            create_task(self.handle_websocket_requests()),
            create_task(self.send_websocket_messages()),
        ]

