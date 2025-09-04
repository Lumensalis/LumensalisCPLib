from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler
__importProfile = getImportProfiler( globals(), reloadable=True  )

from LumensalisCP.HTTP.BSR.common import *

from LumensalisCP.util.Reloadable import ReloadableModule
from LumensalisCP.util.TextIOHelpers import valToJson, v2jSimpleTypes

if TYPE_CHECKING:
    from .BasicServer import BasicServer
    from .WebsocketSession import WebsocketSession

#############################################################################
__importProfile.parsing()

_serverModule = ReloadableModule( 'LumensalisCP.HTTP.BasicServer' )
_BasicServer = _serverModule.reloadableClassMeta('BasicServer')

_sessionModule = ReloadableModule( 'LumensalisCP.HTTP.WebsocketSession' )
_WebsocketSession = _sessionModule.reloadableClassMeta('WebsocketSession')

@_WebsocketSession.reloadableMethod()
def close(self:WebsocketSession) -> None:
    self.infoOut("CLOSING WebsocketSession")
    if self.websocket is not None:
        try:
            self.dbgOut("calling websocket.close()")
            self.websocket.close()
        except Exception as inst:
            self.SHOW_EXCEPTION( inst, "error closing websocket" )
        self.websocket = None
    if self in self.server.websockets:
        self.dbgOut("removing from server.websockets")
        self.server.websockets.remove(self)

    self.dbgOut("session is close")


@_WebsocketSession.reloadableMethod()
def handle_websocket_request(self:WebsocketSession):
    if self.websocket is None or self.websocket.closed:
        return
    
    data = None
    try:
        data = self.websocket.receive(fail_silently=False)
    except Exception as inst:
        self.SHOW_EXCEPTION( inst, "error receiving websocket data %r", data )
        self.close()
        return
    if data is None:
        return
    try:
        self.infoOut( 'websocket data = %r', data )
        jData = json.loads(data)
        main = getMainManager()
        main.handleWsChanges(jData)
    except Exception as inst:
        self.SHOW_EXCEPTION( inst, "error on incoming websocket data %r", data )
        self.close()

_digits = ["0","1","2","3","4","5","6","7","8","9"]
def writeInt( out:TextIO, val:int, pad:int = 0, mag:Optional[int]=None ) -> None:
    if val < 0:
        out.write( '-' )
        val = -val  
    if val >= 10000:
        out.write( _digits[val // 10000] )
        writeInt( out, val % 10000, pad, mag=5 )
    elif val >= 1000:
        out.write( _digits[val // 1000] )
        writeInt( out, val % 1000, pad, mag=mag or 4 )
    elif val >= 100:
        out.write( _digits[val // 100] )
        writeInt( out, val % 100, pad, mag=mag or 3 )
    elif val >= 10:
        out.write( _digits[val // 10] )
        writeInt( out, val % 10, pad, mag=mag or 2 )
    else:
        out.write( _digits[val] )

def writeMonitoredChanges(self:WebsocketSession, out:TextIO, pm:Any, name:str, val:Any  ):
    """
    Generator that yields JSONResponse objects with monitored changes.
    """
    out.write( '"' )
    out.write( name )
    out.write( '":' )
    if type(val) not in v2jSimpleTypes:
        if isinstance(val, str):
            # TODO:
            out.write( '"' )
            out.write( val )
            out.write( '"' )
        elif isinstance(val, bool):
            out.write( 'true' if val else 'false' )
        elif val is None:
            out.write( 'null' )
        else:
            out.write( val )
    elif isinstance(val, int):
        writeInt(out, val)
    else:
        asJson = valToJson(val)
        #self.infoOut( "writeMonitoredChanges %s = (%s)%r on %r", name, type(asJson), asJson, type(out) )
        if isinstance(asJson,int):
            writeInt(out, asJson)
        elif isinstance(asJson,str):
            out.write( '"' )
            out.write( asJson )
            out.write( '"' )
        else:
            out.write( repr(asJson) )

@_WebsocketSession.reloadableMethod()
def updateSocketClient(self:WebsocketSession )->None:
    if self.websocket is None or self.websocket.closed:
        return
   
    jsonBuffer =self._ws_jsonBuffer # type:ignore[reportAttributeAccessIssue]
    checked = 0
    changed = 0
    gc_before = 0

    main = getMainManager()
    context = main.getContext()
    assert jsonBuffer is not None, "jsonBuffer must be set if useStringIO is True"
    #print(f" jsonBuffer:{dir(jsonBuffer)}")
    x = 0
    for mv in main.panel.monitored.values(): 
        v = mv.source
        currentValue = v.getValue(context)
        if currentValue is None:
            if self.enableDbgOut: self.dbgOut( "updateSocketClient %s is None", v.name )
            continue
        checked += 1
        if currentValue != self.priorMonitoredValue.get(v.name,None):
            self.priorMonitoredValue[v.name] = currentValue

            if x == 0:
                gc_before = gc.mem_free()
                jsonBuffer.seek(0)
                jsonBuffer.write("{")
            else:
                jsonBuffer.write(",")
            x += 1
            changed+=1
            writeMonitoredChanges(self, jsonBuffer, mv, v.name, currentValue)
            #for s in yieldMonitoredChanges(self, mv, v.name, currentValue):
            #    jsonBuffer.write(s) # type:ignore[reportAttributeAccessIssue]
    if changed > 0:
        jsonBuffer.write("}")
        message = jsonBuffer.getvalue()[:jsonBuffer.tell()] 
        #print(f"updateSocketClient writing {message}")
        gc_after_message_create = gc.mem_free()
        try:
            self.websocket.send_message(message, fail_silently=True)
        except Exception as inst:
            self.SHOW_EXCEPTION( inst, "error sending websocket message" )
            self.close()
        gc_after = gc.mem_free()
        if self.enableDbgOut:
            self.dbgOut("gc delta for message[%d] is %d / %d (%d)", len(message),
                        gc_after_message_create-gc_before,
                        gc_after-gc_after_message_create,
                        gc_after-gc_before
                        )



__importProfile.complete()