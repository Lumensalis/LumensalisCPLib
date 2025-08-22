from LumensalisCP.ImportProfiler import getImportProfiler
__sayBSR_sakRLImport = getImportProfiler( globals(), reloadable=True )

import re

from LumensalisCP.HTTP.BSR.common import *
from LumensalisCP.util.CountedInstance import CountedInstance
from LumensalisCP.util.Reloadable import ReloadableModule

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    from LumensalisCP.HTTP.BasicServer import BasicServer

_module = ReloadableModule( 'LumensalisCP.HTTP.BasicServer' )
_BasicServer = _module.reloadableClassMeta('BasicServer')


# pyright: reportPrivateUsage=false, reportUnusedImport=false, reportUnusedFunction=false

import microcontroller

from LumensalisCP.util.ObjToDict import objectToDict

#############################################################################

def getAsyncInfo(main:MainManager) -> dict[str, Any]:
    asyncLoop = main.asyncLoop
    asyncManager = main.asyncManager

    children = dict( [(getattr(task,'name',None) or task.dbgName, task.asyncTaskStats()) for task in  asyncManager.children] ) 

    return {
        #'nextWait': asyncLoop.nextWait,
        #'nextRefresh': asyncLoop.nextRefresh,
        'inner': asyncLoop.innerTracker.stats(),
        'priorWhen': asyncLoop.priorSleepWhen,
        'latestSleepDuration': asyncLoop.latestSleepDuration,
        'children' : children,
    }


#############################################################################

class SakActionGroup(DecoratedActionGroupT[Union[Response,None]]):
    pass


sakCmd = SakActionGroup("cmd",prefix="cmd_")

#############################################################################

@sakCmd()
def cmd_resetTrackers(request:BSRRequest):
    main = request.server.main

    print( "resetting trackers" )
    main.asyncLoop.tracker.reset()
    main.asyncLoop.subTracker.reset()
    main.asyncLoop.innerTracker.reset()
    for task in main.asyncManager.children:
        task.tracker.reset()
        task.subTracker.reset()

@sakCmd()
def cmd_set(request:BSRRequest):
    settings:StrAnyDict = request.requestJson.get('settings', None) # type:ignore[reportAttributeAccessIssue]
    assert isinstance(settings,dict)
    
    for tag, value in settings.items():
        assert isinstance(tag, str), f"Expected tag to be a string, got {tag} ({type(tag)})"
        if tag == 'loopMode':
            assert isinstance(value, int), f"Expected loopMode to be an int, got {value} ({type(value)})"
            request.server.main.asyncLoop.loopMode = value
            cmd_resetTrackers(request)
        else:
            raise ValueError(f"Unknown setting tag: {tag}")

#############################################################################
# Status Topics
statusTopic = QueryActionGroup("gsi",prefix="st_")

@statusTopic()
def st_supervisor(request:BSRRequest):
    return {
            'runtime': attrsToDict( supervisor.runtime, ['autoreload','run_reason'] ),
            'ticks_ms': supervisor.ticks_ms()
        } 

@statusTopic()
def st_microcontroller(request:BSRRequest):
    return dict(
           cpu = objectToDict(microcontroller.cpu)
    )

@statusTopic()
def st_gc(request:BSRRequest) -> Any:
    return attrsToDict( gc, ['enabled','mem_alloc','mem_free'] )

@statusTopic()
def st_main(request:BSRRequest) -> Any:
    main = request.server.main
    context = main.getContext()
    return attrsToDict( main, ['cycle','when','newNow'],
            context = attrsToDict( context, ['updateIndex','when'] ),
            scenes = attrsToDict( main.scenes,["currentScenes"] ),
            # nextWait = main.asyncLoop.nextWait, # type: ignore
            nextRefresh  = main.asyncLoop.nextRefresh, # type: ignore
            priorWhen = main.asyncLoop.priorSleepWhen, # type: ignore
            #priorSleepDuration = main.__priorSleepDuration, # type: ignore
            latestSleepDuration = main.asyncLoop.latestSleepDuration # type: ignore
        )

@statusTopic()
def st_misc( request:BSRRequest ) -> Any:
    return {
            'instanceCounts': CountedInstance._getCiInstanceCounts()
        }

@statusTopic()
def st_profiler( request:BSRRequest ) -> Any:
    return request.server.main.profiler.getProfilerInfo( dumpConfig=None )

@statusTopic()
def st_monitored( request:BSRRequest ):
    return dict( [ (mv.source.name, inputSourceSnapshot(mv.source)) for mv in request.server.main.panel.monitored.values() ] )

@statusTopic()
def st_asyncLoop( request:BSRRequest ) -> Any:
    main = request.server.main
    return getAsyncInfo(main)

@statusTopic()
def st_refreshables( request:BSRRequest ) -> Any:
    main = request.server.main
    rv:StrAnyDict = {}
    for refreshable in main.refreshables:
        #continue
        rv[refreshable.dbgName] = {
            'nextRefresh': refreshable.nextRefresh,
            'refreshCount': refreshable.refreshCount,
            'exceptionCount': refreshable.exceptionCount,
        }
    return rv

#############################################################################
__pathRx = re.compile(r'^(([\.]?[a-zA-Z_][a-zA-Z_0-9]*)|(\[[^\]]+\])|(\([^\)]*\)))(.*)$')
__intIndex = re.compile(r'^([-]?[0-9]+)$')
def getInstance( request:BSRRequest, path:str ) -> Any:

    m = __pathRx.match(path)
    if m is None:
        raise ValueError(f"Invalid path: {path}")
    groups = m.groups()
    main = request.server.main
    tag = groups[0]
    leftover = groups[-1]
    main.infoOut(f"getInstance: {path} / {tag} : {groups} leftover={leftover}")
    v:Any = getattr(main, tag , None)
    if v is None:
        assert main._renameIdentifiablesItems is not None
        v = main._renameIdentifiablesItems.get(tag, None)
    assert v is not None, f"getInstance: {path} : {tag} not found"
    while leftover != '':
        m = __pathRx.match(leftover)
        assert m is not None, f"getInstance: {path} : {leftover} does not match pathRx"
        groups = m.groups()
        tag = groups[0]
        leftover = groups[-1]
        main.infoOut(f"getInstance: .... {tag} : {groups} leftover={leftover}")
        if tag.startswith('[') and tag.endswith(']'):
            index = tag[1:-1]
            if __intIndex.match(index):
                index = int(index)
            v = v[index]
        elif tag.startswith('(') and tag.endswith(')'):
            assert callable(v), f"getInstance: {path} : {tag} is not callable, but {type(v)}"
            interior = tag[1:-1]
            if len(interior) == 0:
                v = v()
            else:
                v = v(interior)
        elif tag.startswith('.'):
            v = getattr(v, tag[1:], None)
        else:
            raise ValueError(f"Invalid tag in path: {tag} in {path}")

        assert v is not None, f"getInstance: {path} : {tag} not found"
    
    main.infoOut(f"getInstance: {path} returning ({type(v)})")
    return v

#############################################################################

def getStatusInfo(request:BSRRequest, tags:Optional[list[str]] = None) -> dict[str, Any]:
    #main = self.main
    #context = main.getContext()
    rv:StrAnyDict =  {}

    for tag, func in statusTopic.matching(tags):
        rv[tag] = valToJson(func(request))
    rv['request'] = {
        'path': request.request.path,
        'query_params': str(request.request.query_params),
    }

    return rv

#############################################################################

lsTopic = QueryActionGroup("ls",prefix="ls_")

@lsTopic()
def ls_topics(request:BSRRequest) -> Any:
    return list(statusTopic.actionNames())

#############################################################################

@_BasicServer.reloadableMethod()
def BSR_sak(self:BasicServer, request:Request) -> JSONResponse | Response:
    """
    Serve a default static plain text message.
    """
    
    try:
        # Get objects
        sakRequest = BSRRequest(self,request)

        if request.method == GET:
            
            return JSONResponse(request, getStatusInfo(sakRequest) )

        
        # Upload or update objects
        if request.method in {POST, PUT}:
            requestJson:StrAnyDict = request.json() # type:ignore[reportAttributeAccessIssue]
            assert requestJson is not None, "requestJson is None"
            self.infoOut( "BSR_sak requestJson = %s", requestJson )
            #result:StrAnyDict = {}
            if 'autoreload' in requestJson:
                autoreload:bool = requestJson['autoreload'] # type:ignore[reportAttributeAccessIssue]
                self.infoOut( "setting autoreload to %r", autoreload )
                supervisor.runtime.autoreload = autoreload

            if 'cmd' in requestJson:
                sakCmd.invoke( sakRequest )
                
            if (path := requestJson.get('path', None)) is not None:
                instance = getInstance( sakRequest, path )
                if instance is not None:
                    if isinstance(instance, (int, str, bool, float,type(None)) ):
                        sakRequest.result['instance'] = instance
                    else:    
                        sakRequest.result['instance'] = {
                            'repr' : repr(instance),
                            'type' : str(type(instance)),# type: ignore
                            'id': id(instance),
                        } 


            if (enableDebug := requestJson.get('enableDebug',None)) is not None:
                instance =  getInstance( sakRequest, enableDebug )
                instance.enableDbgOut = True

            if (disableDebug := requestJson.get('disableDebug',None)) is not None:
                instance =  getInstance( sakRequest, disableDebug )
                instance.enableDbgOut = False


            if gsi := requestJson.get('getStatusInfo',False):
                self.infoOut( "gsi = %r in (%s)%r", gsi, type(requestJson), requestJson   )
                if isinstance(gsi, bool):
                    assert gsi 
                    sakRequest.result['status'] = statusTopic.gather(sakRequest,None)
                else:
                    sakRequest.result['status'] = statusTopic.gather(sakRequest, gsi)

            ls:Any
            if ls := requestJson.get('ls',None) is not None:
                sakRequest.result['ls'] = lsTopic.gather(sakRequest, ls)
            
            response =  sakRequest.makeResponse()
            self.infoOut( "BSR_sak response = %s", response )
            return response

        else:
            self.errOut( "Unsupported request method %s", request.method )
            return JSONResponse(request, {"error": f"Unsupported request method {request.method}"}, status=(405,"Unsupported"))
        return JSONResponse(request, getStatusInfo(self, request) )
    except Exception as inst:
        return ExceptionResponse(request, inst, "sak failed" )
    return JSONResponse(request, {"message": "Something went wrong"})


__sayBSR_sakRLImport.complete()

