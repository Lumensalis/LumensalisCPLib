
from LumensalisCP.IOContext import *
from LumensalisCP.commonCPWifi import *
from LumensalisCP.pyCp.importlib import reload
from . import BasicServer

#print()
#print( f"----------------------" )
print( f"importing {__name__}..." )
#print( f"----------------------" )
#print()

from adafruit_httpserver import DELETE, GET, POST, PUT, JSONResponse, Request, Response

_v2jSimpleTypes = { int, str, bool, float,type(None) }
def valToJson( val ):
    if type(val) in _v2jSimpleTypes: return val
    if callable(val):
        try:
            return valToJson( val() )
        except: pass
    if isinstance( val, dict ):
        return dict( [ (tag, valToJson(v2)) for tag,v2 in val.items() ])

    if isinstance( val, list ):
        return [ valToJson(v2) for v2 in val ]
    return repr(val)

def attrsToDict( obj, attrList, **kwds ):
    rv = dict(kwds)
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

def getStatusInfo(self:BasicServer.BasicServer, request:Request ):
    main = self.main
    context = main.getContext()
    rv =  {
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
                nextWait = main._nextWait,
                priorWhen = main.__priorSleepWhen,
                latestSleepDuration = main.__latestSleepDuration
            )
            
        }
    return rv

class QueryConfig(object):
    fillParents:bool = False
    recurseChildren:bool|None=None
    includeName:bool = False
    includeId:bool = True
    includeType:bool = True
    
def getQueryResult( target:NamedLocalIdentifiable, path:list[str], qConfig:QueryConfig|None=None ):
    rv = None
    if qConfig is None: qConfig=QueryConfig()
    if len(path):
        child = target.nliFind(path[0])
        if child is None: return { "missing child" : path[0]}
        rv = { child.name : getQueryResult( child, path[1:], qConfig )  }
        if not qConfig.fillParents: return rv
    else: 
        rv = {}
    name = getattr(target,"name",None)
    if qConfig.includeName and name is not None: rv['name'] = name
    if qConfig.includeType and not isinstance(target,NamedLocalIdentifiableContainerMixin):  rv["type"] = type(target).__name__
    if qConfig.includeId: rv["localId"] = target.localId
    oldRecurseChildren = qConfig.recurseChildren
    try:
        if len(path) == 0 and qConfig.recurseChildren is None: qConfig.recurseChildren = True
        localRecurseChildren = qConfig.recurseChildren # and not len(path)
        containers = target.nliGetContainers() 
        if containers is not None and len( items:=list(containers)) > 0: 
            if localRecurseChildren:
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
        rv["kind"] = type(target).__name__
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


def _reloadAll( ):
    from LumensalisCP.Main import ManagerRL
    from . import BasicServerRL            
    modules = [ ManagerRL, BasicServerRL ]
    for m in modules:
        reload( m )
    return modules

    
def BSR_cmd(self:BasicServer.BasicServer, request:Request, cmd:str=None, **kwds ):
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
        if cmd == "reloadAll":
            modules = _reloadAll()
            
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
            requestJson = request.json()
            if 'autoreload' in requestJson:
                autoreload = requestJson['autoreload']
                self.infoOut( "setting autoreload to %r", autoreload )
                supervisor.runtime.autoreload = autoreload


        return JSONResponse(request, getStatusInfo(self, request) )
    except Exception as inst:
        return ExceptionResponse(request, inst, "sak failed" )
    return JSONResponse(request, {"message": "Something went wrong"})
    
    
def BSR_client(self:BasicServer.BasicServer, request: Request):
    
    print( f"get /client with {[v.name for v in self.monitoredVariables]}")
    vb = self.cvHelper.varBlocks(self.monitoredVariables)
    parts = [
        self.HTML_TEMPLATE_A,
        vb['htmlParts'],
        self.HTML_TEMPLATE_B,
        vb['jsSelectors'],
        
        vb['wsReceived'],
        
        self.HTML_TEMPLATE_Z,
    ]
    html = "\n".join(parts)
    
    return Response(request, html, content_type="text/html")
    