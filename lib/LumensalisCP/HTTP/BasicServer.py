# SPDX-FileCopyrightText: 2023 Michał Pokusa
# SPDX-FileCopyrightText: 2025 James Fowler
#
# SPDX-License-Identifier: Unlicense

from __future__ import annotations
from LumensalisCP.ImportProfiler import  getImportProfiler
__sayHTTPBasicServerImport = getImportProfiler( __name__, globals() ) 

# pyright: reportUnusedImport=false, reportUnusedVariable=false

from LumensalisCP.Main.Async import MainAsyncChild, ManagerAsync


from LumensalisCP.IOContext import *


from LumensalisCP.pyCp.importlib import reload
from LumensalisCP.HTTP import BasicServerRL
from LumensalisCP.HTTP import ControlVarsRL
from LumensalisCP.HTTP.BSR import BSR_profileRL
from LumensalisCP.HTTP.BSR import BSR_sakRL
from LumensalisCP.HTTP.BSR import BSR_cmdRL

from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl
from LumensalisCP.util.Reloadable import addReloadableClass, reloadingMethod

from LumensalisCP.HTTP._httpBits import *

#############################################################################
__sayHTTPBasicServerImport.parsing()

class BasicServer(Server,MainAsyncChild):
    
    # type:ignore[unused-function]
    # type: ignore[reportUntypedFunctionDecorator,reportUnusedFunction]

    def __init__( self, **kwds:Unpack[MainAsyncChild.KWDS] ) -> None:

        kwds.setdefault('name', 'LCPFWebServer')
        MainAsyncChild.__init__(self, **kwds )
        assert self.main is not None
        main = self.main 

        self.pool = main.socketPool
        Server.__init__(self, self.pool, debug=pmc_mainLoopControl.enableHttpDebug )

        # TODO: make actual client instance for multiple connections...???
        self.websocket: Websocket|None = None
        self.cvHelper:ControlVarsRL.PanelControlTemplateHelper|None = ControlVarsRL.PanelControlTemplateHelper( main=main )

        #self.main = main
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


    def asyncTaskStats(self, out:Optional[dict[str,Any]]=None) -> dict[str,Any]:
        rv = super().asyncTaskStats(out)
        rv['monitoredVariables'] = [v.name for v in self.monitoredVariables]
        rv['ipAddress'] = str(wifi.radio.ipv4_address)
        return rv
            
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
        moduleName = f'BSR_{name}RL'
        
        def handler(request: Request,reloading:bool=False,**kwds:StrAnyDict):
            try:
                module = globals().get(moduleName,None)
                if module is not None:
                    c = getattr( module, functionName, None )
                    assert c is not None, f"missing reloadable {moduleName}.{functionName}" 
                else:
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
            
            #reload( ControlVarsRL )
            BasicServerRL._reloadForRoute(self,name) # type:ignore[call-arg]
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
        self.addReloadableRouteHandler( "profile" )
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
        
    @reloadingMethod
    def updateSocketClient(self, useStringIO:bool=False )->None:...

    @reloadingMethod
    def handle_websocket_request(self): ...

    #########################################################################
    async def runAsyncSetup(self) -> None:
        self.startupOut( f"{self.__class__.__name__} serverLoop starting" )
        self.useStringIO = False
        self._ws_jsonBuffer:io.StringIO|None = io.StringIO(8192) if self.useStringIO else None # type:ignore[assignment]
    
        socket = self.main.socketPool
        self.startupOut( "socketPool=%r", socket )
        address = wifi.radio.ipv4_address
        assert address is not None, f"wifi.radio.ipv4_address is None, cannot start {self.__class__.__name__} server"
        address = str(address)
        self.startupOut( "starting server on %r", address )
        self.start(address) 
        self.startupOut( "started server on %r", address )


    async def runAsyncSingleLoop(self) -> None:
        try:
            if self.websocket is not None and self.websocket.closed:
                self.handle_websocket_request()
                await self.sleep(0.05)
                self.updateSocketClient(self.useStringIO)
                await self.sleep(0.05)
            
            pool_result = self.poll()
            if pool_result == adafruit_httpserver.REQUEST_HANDLED_RESPONSE_SENT:
                # Do something only after handling a request
                self.infoOut( "handle_http_requests handled request")
                pass
            await self.sleep(0.05)

        except KeyboardInterrupt as error:
            self.asyncManager.childExceptionExit(self, error) 
            raise
        except Exception as error:
            self.SHOW_EXCEPTION( error, 'handle_http_requests error' )
            await self.sleep(0.25)
        #print( "handle_http_requests sleep..")
        await self.sleep(0.05)


addReloadableClass(BasicServer)

__sayHTTPBasicServerImport.complete(globals())
