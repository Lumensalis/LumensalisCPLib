# SPDX-FileCopyrightText: 2023 Michał Pokusa
#
# SPDX-License-Identifier: Unlicense

from asyncio import create_task, gather, run, sleep as async_sleep
import socketpool
import wifi
import json
import mdns

import adafruit_httpserver
from adafruit_httpserver import Server, Request, Response, Websocket, GET

from .ControlVars import ControlValueTemplateHelper

class BasicServer(Server):
    
    def __init__( self, *args, main=None, **kwds ):
        
        assert main is not None
        
        self.pool = socketpool.SocketPool(wifi.radio)
        super().__init__(self.pool, debug=True)


        #pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

        self.websocket: Websocket = None
        self.cvHelper = ControlValueTemplateHelper( main=main )

        self.main = main
        self.monitoredVariables = []
        self.priorMonitoredValue = {}
        self._setupRoutes()
        
        TTCP_HOSTNAME = main.config.options.get('TTCP_HOSTNAME',None)
        print(f"BasicServer TTCP_HOSTNAME = {TTCP_HOSTNAME}")
        #if (TTCP_HOSTNAME := main.config.options.get('TTCP_HOSTNAME',None)) is not None:
        if TTCP_HOSTNAME is not None:
            print(f"setting HOSTNAME to {TTCP_HOSTNAME}")
            self.mdns_server = mdns.Server(wifi.radio)
            self.mdns_server.hostname = TTCP_HOSTNAME
            self.mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=5000)
        
    def monitorControlVariable( self, v ):
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

    def _setupRoutes(self):
        print( "_setupRoutes" )
        
        
        @self.route("/client", GET)
        def client(request: Request):
            
            vb = self.cvHelper.varBlocks()
            parts = [
                self.HTML_TEMPLATE_A,
                vb['htmlParts'],
                self.HTML_TEMPLATE_B,
                vb['jsSelectors'],
                
                vb['wsReceiveds'],
                
                self.HTML_TEMPLATE_Z,
            ]
            html = "\n".join(parts)
            
            return Response(request, html, content_type="text/html")


        @self.route("/connect-websocket", GET)
        def connect_client(request: Request):
            #global websocket  # pylint: disable=global-statement

            if self.websocket is not None:
                self.websocket.close()  # Close any existing connection

            self.websocket = Websocket(request)

            return self.websocket
        
        
        @self.route("/")
        def base(request: Request):
            """
            Serve a default static plain text message.
            """
            print( "base request...")
            return Response(request, "Hello from the CircuitPython HTTP Server!")
        
    async def handle_http_requests(self):
        try:
            
            while True:
                #print( "handle_http_requests poll..")
                pool_result = self.poll()
                if pool_result == adafruit_httpserver.REQUEST_HANDLED_RESPONSE_SENT:
                    # Do something only after handling a request
                    print( "handle_http_requests handled request")
                    pass
                
                #print( "handle_http_requests sleep..")
                await async_sleep(0.05)
    
        except Exception  as error:
            print( f'handle_http_requests error {error}' )
            

    async def handle_websocket_requests(self):
        try:
            print( 'handle_websocket_requests starting' )
            while True:
                if self.websocket is not None:
                    if (data := self.websocket.receive(fail_silently=True)) is not None:
                        
                        try:
                            # print( f'websocket data = {data}' )
                            jdata = json.loads(data)
                            self.main.handleWsChanges(jdata)
                        except Exception as inst:
                            print( f"error on incoming websocket data {data} : {inst}")
                        #r, g, b = int(data[1:3], 16), int(data[3:5], 16), int(data[5:7], 16)
                        #print( f'fill {(r, g, b)}')
                        #pixel.fill((r, g, b))

                await async_sleep(0.05)
        except Exception  as error:
            print( f'handle_websocket_requests error {error}' )


    async def send_websocket_messages(self):
        
        try:
            while True:
                if self.websocket is not None:
                    payload = {}
                    for v in self.monitoredVariables:
                        if v.value != self.priorMonitoredValue.get(v.name,None):
                            payload[v.name] = v.value
                            self.priorMonitoredValue[v.name] = v.value
                    if len(payload):
                        message = json.dumps( payload )
                        print( "writing WS update : " + message )
                        self.websocket.send_message(message, fail_silently=True)
                await async_sleep(0.5)
        except Exception  as error:
            print( f'send_websocket_messages error {error}' )


    def createAsyncTasks( self ):
        print( "createAsyncTasks... " )

        return [
            create_task(self.handle_http_requests()),
            create_task(self.handle_websocket_requests()),
            create_task(self.send_websocket_messages()),
        ]

