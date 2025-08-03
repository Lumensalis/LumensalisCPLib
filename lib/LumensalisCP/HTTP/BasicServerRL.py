from LumensalisCP.ImportProfiler import getImportProfiler
__sayHTTPBasicServerRLImport = getImportProfiler( "HTTP.BasicServerRL", globals(), reloadable=True )

from LumensalisCP.ImportProfiler import ImportProfiler, ReloadableImportProfiler

from .BSR.common import *
import traceback
from LumensalisCP.IOContext import *
from LumensalisCP.commonCPWifi import *
    
from LumensalisCP.util.Reloadable import ReloadableModule

#############################################################################
# pyright: ignore[reportUnusedImport]

#from LumensalisCP.HTTP.BSR.BSR_profileRL import BSR_profile 

_module = ReloadableModule( 'LumensalisCP.HTTP.BasicServer' )
_BasicServer = _module.reloadableClassMeta('BasicServer')

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

def BSR_query(self:BasicServer, request:Request, name:str):
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

from LumensalisCP.Main import ProfilerRL
from LumensalisCP.HTTP.BSR import BSR_profileRL
from LumensalisCP.HTTP.BSR import BSR_sakRL
from LumensalisCP.HTTP.BSR import BSR_cmdRL

def _reloadForRoute( self:BasicServer, name:str ) -> None: # type:ignore[no-untyped-def]

    from LumensalisCP.HTTP import BasicServerRL
    modules: list[Any] = [  ]
    ImportProfiler.SHOW_IMPORTS = True
    ReloadableImportProfiler.SHOW_IMPORTS = True
    
    
    self.infoOut( "_reloadForRoute %s", name )
    pmc_gcManager.checkAndRunCollection(force=True)

    if "profile" in name:
        modules.extend( [ProfilerRL,  BSR_profileRL] )
    elif "sak" in name:
        modules.extend( [BSR_sakRL] )
    elif "cmd" in name:
        modules.extend( [BSR_cmdRL] )

    
    modules.append( BasicServerRL )

    self.infoOut( "reloading  %s", modules )
    
    for module in modules:
        reload( module )
    pmc_gcManager.checkAndRunCollection(force=True)
    self.infoOut( "_reloadForRoute %s complete", name )
    
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
        # print( f'websocket data = {data}' )
        jData = json.loads(data)
        self.main.handleWsChanges(jData)
    except Exception as inst:
        self.SHOW_EXCEPTION( inst, "error on incoming websocket data %r", data )

@_BasicServer.reloadableMethod()
def updateSocketClient(self:BasicServer, useStringIO:bool=False )->None:
    if self.websocket is None or self.websocket.closed:
        return
    
    payload = None
    jsonBuffer =self._ws_jsonBuffer # type:ignore[reportAttributeAccessIssue]
     
    checked = 0
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
            jsonBuffer.seek(0) # type:ignore[reportAttributeAccessIssue]
            jsonBuffer.truncate() # type:ignore[reportAttributeAccessIssue]
            json.dump( payload, jsonBuffer ) # type:ignore[reportAttributeAccessIssue]
            message = jsonBuffer.getvalue() # type:ignore[reportAttributeAccessIssue]
        else:
            message =json.dumps(payload)
        self.websocket.send_message(message, fail_silently=True)
        if self.enableDbgOut: self.dbgOut( "wrote WS update : %r", message ) 


__sayHTTPBasicServerRLImport.complete(globals())
