
import traceback
from LumensalisCP.IOContext import *
from LumensalisCP.commonCPWifi import *
from LumensalisCP.pyCp.importlib import reload
from LumensalisCP.HTTP import BasicServer

import LumensalisCP.HTTP.ControlVarsRL

#from adafruit_httpserver import DELETE, GET, POST, PUT, JSONResponse, Request, Response  # pyright: ignore[reportMissingImports|reportAttributeAccessIssue]
from adafruit_httpserver import DELETE, GET, POST, PUT, JSONResponse, Request, Response  # pyright: ignore

_v2jSimpleTypes:set[type] = { int, str, bool, float,type(None) }

def valToJson( val:Any ) -> Any:
    if type(val) in _v2jSimpleTypes: return val
    if callable(val):
        try:
            return valToJson( val() )
        except: pass
    if isinstance( val, dict ):
        return dict( [ (tag, valToJson(v2)) for tag,v2 in val.items() ]) # type:ignore[return-value]

    if isinstance( val, list ):
        return [ valToJson(v2) for v2 in val ] # type:ignore[return-value]
    return repr(val)

def attrsToDict( obj:Any, attrList:list[str], **kwds:StrAnyDict ) -> StrAnyDict:
    rv:StrAnyDict = dict(kwds)
    for attr in attrList:
        rv[attr] = valToJson( getattr(obj,attr,None) )
    return rv

#############################################################################

def ExceptionResponse( request: Request, inst:Exception, message:Optional[str]=None ) -> Response:
    return JSONResponse( request,
        { 'exception' : str(inst),
            'message': message or f"unhandled exception",
            'traceback' : traceback.format_exception(inst) 
         }
    )
    
#############################################################################
def inputSourceSnapshot( input:InputSource ) -> dict[str,Any]:
    return dict(
        value= valToJson( input.getValue() ),
        lc=input.latestChangeIndex,
        lu=input.latestUpdateIndex,
        localId=input.localId,
        cls = input.__class__.__name__,
    )

def getStatusInfo(self:BasicServer.BasicServer, request:Request ) -> dict[str, Any]:
    main = self.main
    context = main.getContext()
    monitoredInfo = [ 
        #(i.name, inputSourceSnapshot(i)) for i in main._monitored
        (mv.source.name, inputSourceSnapshot(mv.source)) for mv in main.panel.monitored.values()
    ]

    monitored = dict( monitoredInfo  )
    rv:StrAnyDict =  {
            'supervisor': {
                'runtime': attrsToDict( supervisor.runtime, ['autoreload','run_reason'] ),
                'ticks_ms': supervisor.ticks_ms()
            },
            'request': {
                'path': request.path,
                'query_params': str(request.query_params),
            },
            'gc': attrsToDict( gc, ['enabled','mem_alloc','mem_free'] ), 
            'main': attrsToDict( main, ['cycle','when','newNow'],
                context = attrsToDict( context, ['updateIndex','when'] ),
                scenes = attrsToDict( main.scenes,["currentScenes"] ),
                nextWait = main._nextWait, # type: ignore
                priorWhen = main.__priorSleepWhen, # type: ignore
                #priorSleepDuration = main.__priorSleepDuration, # type: ignore
                latestSleepDuration = main.__latestSleepDuration # type: ignore
            ),
            'monitored': monitored
        }
    return rv

class QueryConfig(object):
    fillParents:bool = False
    recurseChildren:Optional[bool]=None
    includeName:bool = False
    includeId:bool = True
    includeType:bool = True

def getQueryResult( target:NliInterface|NliContainerBaseMixin, path:list[str], qConfig:Optional[QueryConfig]=None ) -> Any: 
    rv = None
    if qConfig is None: qConfig=QueryConfig()
    if len(path):
        assert isinstance(target,NamedLocalIdentifiable)
        child = target.nliFind(path[0])
        if child is None: return { "missing child" : path[0]}
        assert isinstance(child,NliContainerBaseMixin), f"child {path[0]} is not a NliContainerMixinBaseMixin, but {type(child)}"
        rv = { child.containerName : getQueryResult( child, path[1:], qConfig )  }
        if not qConfig.fillParents: return rv
    else: 
        rv = {}
    name = getattr(target,"name",None)
    if qConfig.includeName and name is not None: rv['name'] = name
    if qConfig.includeType and not isinstance(target,NliContainerMixin):  rv["type"] = type(target).__name__
    if qConfig.includeId and hasattr(target,'localId'): rv["localId"] = target.localId # type: ignore
    oldRecurseChildren = qConfig.recurseChildren
    try:
        if len(path) == 0 and qConfig.recurseChildren is None: qConfig.recurseChildren = True
        localRecurseChildren = qConfig.recurseChildren # and not len(path)
        containers = target.nliGetContainers() #
        if containers is not None and len( items:=list(containers)) > 0: 
            if localRecurseChildren:
                c:NliContainerBaseMixin
                for c in items:
                    cv = getQueryResult(c,[],qConfig=qConfig)
                    if len(cv): 
                        rv[c.name] = cv
            else:
                rv['containers'] = [(getQueryResult(c,[],qConfig=qConfig) if localRecurseChildren else c.name) for c in items ]
                
        children= target.nliGetChildren()
        if children is not None and len( items:=list(children)) > 0:
            if localRecurseChildren:
                for c in items:
                    v= getQueryResult(c,[],qConfig=qConfig)
                    #if len(v): 
                    rv[c.name] = v
            else:            
                rv['children'] = [(getQueryResult(c,[],qConfig=qConfig) if localRecurseChildren else c.name) for c in items ]
    except Exception as inst:
        rv['exception'] = {
            'message' : str(inst),
            'traceback' : traceback.format_exception(inst) ,
        }
        rv["kind"] = target.__class__.__name__ # type:ignore[reportUnknownMemberType]
    finally:
         qConfig.recurseChildren = oldRecurseChildren
         
    return rv        


def BSR_query(self:BasicServer.BasicServer, request:Request, name:str):
    """
    """
    
    try:
        # Get objects
        if name ==  '.':
            result = getQueryResult( self.main, [] )
        else:
            result = getQueryResult( self.main, name.split('.') )
        
        return JSONResponse(request, result )
    
    except Exception as inst:
        return ExceptionResponse(request, inst)
    return JSONResponse(request, {"message": "Something went wrong"})


def _reloadAll(self:BasicServer.BasicServer ):
    from LumensalisCP.Main import ManagerRL
    from LumensalisCP.HTTP import BasicServerRL
    from LumensalisCP.HTTP import ControlVarsRL
    modules = [ ManagerRL, BasicServerRL, ControlVarsRL ]
    for m in modules:
        reload( m )
    self.cvHelper = None
    return modules

def BSR_cmd(self:BasicServer.BasicServer, request:Request, cmd:Optional[str]=None, **kwds:StrAnyDict ) -> JSONResponse | Response:
    """
    """
    
    try:
        # Get objects
        print( f"BSR_cmd cmd={repr(cmd)} received...")
        if cmd == "restart":
            def restart():
                print( "restarting" )
                supervisor.reload()
                
            self.main.callLater( restart )
            return JSONResponse(request, { "action":"restarting"} )
        
        if cmd == "reset":
            def reset():
                print( "resetting" )
                microcontroller.reset()
                
            self.main.callLater( reset )
            return JSONResponse(request, { "action":"resetting"} )
        
        if cmd == "reloadAll":
            modules = _reloadAll(self)
            
            return JSONResponse(request, {
                    "action":"reloading",
                    "modules": [m.__name__ for m in modules]                      
                        } )
            
        return JSONResponse(request, {"unknown command":cmd} )
    
    except Exception as inst:
        return ExceptionResponse(request, inst, "cmd failed" )
    
    return JSONResponse(request, {"message": "oops, command not handled..."})

def BSR_sak(self:BasicServer.BasicServer, request:Request):
    """
    Serve a default static plain text message.
    """
    
    try:
        # Get objects
        if request.method == GET:
            
            return JSONResponse(request, getStatusInfo(self, request) )

        # Upload or update objects
        if request.method in {POST, PUT}:
            requestJson = request.json() # type:ignore[reportAttributeAccessIssue]
            if requestJson is not None and 'autoreload' in requestJson:
                autoreload:bool = requestJson['autoreload'] # type:ignore[reportAttributeAccessIssue]
                self.infoOut( "setting autoreload to %r", autoreload )
                supervisor.runtime.autoreload = autoreload


        return JSONResponse(request, getStatusInfo(self, request) )
    except Exception as inst:
        return ExceptionResponse(request, inst, "sak failed" )
    return JSONResponse(request, {"message": "Something went wrong"})



def handle_websocket_request(self:BasicServer.BasicServer):
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
        # print( f'websocket data = {data}' )
        jdata = json.loads(data)
        self.main.handleWsChanges(jdata)
    except Exception as inst:
        self.SHOW_EXCEPTION( inst, "error on incoming websocket data %r", data )

def updateSocketClient(self:BasicServer.BasicServer, useStringIO:bool=False )->None:
    if self.websocket is None or self.websocket.closed:
        return
    
    payload = None
    jsonBuffer =self._ws_jsonBuffer # type:ignore[reportAttributeAccessIssue]
     
    checked = 0
    for mv in self.main.panel.monitored.values():
        v = mv.source
        currentValue = v.getValue()
        assert currentValue is not None
        checked += 1
        if currentValue != self.priorMonitoredValue.get(v.name,None):
            if payload is None: payload = {}
            if self.enableDbgOut: self.dbgOut( "updateSocketClient %s changed to %r", v.name, currentValue )
            if type(currentValue) not in _v2jSimpleTypes:
                currentValue = valToJson(currentValue)

            payload[v.name] = currentValue
            self.priorMonitoredValue[v.name] = currentValue
    if self.enableDbgOut: self.infoOut( "updateSocketClient checked %d variables" % checked )

    if payload is not None:
        if useStringIO:
            jsonBuffer.seek(0) # type:ignore[reportAttributeAccessIssue]
            jsonBuffer.truncate() # type:ignore[reportAttributeAccessIssue]
            json.dump( payload, jsonBuffer ) # type:ignore[reportAttributeAccessIssue]
            message = jsonBuffer.getvalue() # type:ignore[reportAttributeAccessIssue]
        else:
            message =json.dumps(payload)
        self.websocket.send_message(message, fail_silently=True)
        if self.enableDbgOut: self.dbgOut( "wrote WS update : %r", message ) 