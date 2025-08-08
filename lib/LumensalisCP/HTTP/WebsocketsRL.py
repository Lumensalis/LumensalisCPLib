from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler
__importProfile = getImportProfiler( globals(), reloadable=True  )

from LumensalisCP.HTTP.BSR.common import *

from LumensalisCP.util.Reloadable import ReloadableModule

_module = ReloadableModule( 'LumensalisCP.HTTP.BasicServer' )
_BasicServer = _module.reloadableClassMeta('BasicServer')

    
@_BasicServer.reloadableMethod()
def handle_websocket_request(self:BasicServer):
    if self.websocket is None or self.websocket.closed:
        return
    
    data = None
    try:
        data = self.websocket.receive(fail_silently=False)
    except Exception as inst:
        self.SHOW_EXCEPTION( inst, "error receiving websocket data %r", data )
        self.websocket.close()
        self.websocket = None
        return
    if data is None:
        return
    try:
        self.infoOut( 'websocket data = %r', data )
        jData = json.loads(data)
        self.main.handleWsChanges(jData)
    except Exception as inst:
        self.SHOW_EXCEPTION( inst, "error on incoming websocket data %r", data )

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

def writeMonitoredChanges(self:BasicServer, out:TextIO, pm:Any, name:str, val:Any  ):
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

@_BasicServer.reloadableMethod()
def updateSocketClient(self:BasicServer, useStringIO:bool=False )->None:
    if self.websocket is None or self.websocket.closed:
        return
    
    payload = None
    jsonBuffer =self._ws_jsonBuffer # type:ignore[reportAttributeAccessIssue]
    checked = 0
    changed = 0
    if useStringIO:
        assert jsonBuffer is not None, "jsonBuffer must be set if useStringIO is True"
        #print(f" jsonBuffer:{dir(jsonBuffer)}")
        x = 0
        for mv in self.main.panel.monitored.values(): 
            v = mv.source
            currentValue = v.getValue()
            if currentValue is None:
                if self.enableDbgOut: self.dbgOut( "updateSocketClient %s is None", v.name )
                continue
            checked += 1
            if currentValue != self.priorMonitoredValue.get(v.name,None):
                self.priorMonitoredValue[v.name] = currentValue
                if x == 0:
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
            self.websocket.send_message(message, fail_silently=True)
        return
    else:
        for mv in self.main.panel.monitored.values():

            v = mv.source
            currentValue = v.getValue()
            if currentValue is None:
                if self.enableDbgOut: self.dbgOut( "updateSocketClient %s is None", v.name )
                continue
            checked += 1
            if currentValue != self.priorMonitoredValue.get(v.name,None):
                if payload is None: payload = {}
                if self.enableDbgOut: self.dbgOut( "updateSocketClient %s changed to %r", v.name, currentValue )
                if type(currentValue) not in v2jSimpleTypes:
                    currentValue = valToJson(currentValue)

                payload[v.name] = currentValue
                self.priorMonitoredValue[v.name] = currentValue
        if self.enableDbgOut: self.infoOut( "updateSocketClient checked %d variables" % checked )

        if payload is not None:
            if useStringIO:
                #print(f" jsonBuffer:{dir(jsonBuffer)}")
                jsonBuffer.seek(0) # type:ignore[reportAttributeAccessIssue]
                #jsonBuffer.truncate() # type:ignore[reportAttributeAccessIssue]
                json.dump( payload, jsonBuffer ) # type:ignore[reportAttributeAccessIssue]
                message = jsonBuffer.getvalue()[:jsonBuffer.tell()] # type:ignore[reportAttributeAccessIssue]
            else:
                message =json.dumps(payload)
            self.websocket.send_message(message, fail_silently=True)
            if self.enableDbgOut: self.dbgOut( "wrote WS update : %r", message ) 



__importProfile.complete()