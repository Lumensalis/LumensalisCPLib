from LumensalisCP.ImportProfiler import getImportProfiler
__sayBSR_sakRLImport = getImportProfiler( globals(), reloadable=True )

from LumensalisCP.HTTP.BSR.common import *
from LumensalisCP.util.CountedInstance import CountedInstance
from LumensalisCP.util.Reloadable import ReloadableModule

_module = ReloadableModule( 'LumensalisCP.HTTP.BasicServer' )
_BasicServer = _module.reloadableClassMeta('BasicServer')

# pyright: reportPrivateUsage=false, reportUnusedImport=false, reportUnusedFunction=false

import microcontroller

from LumensalisCP.util.ObjToDict import objectToDict


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


def resetTrackers(main:MainManager) -> None:
    print( "resetting trackers" )
    main.asyncLoop.tracker.reset()
    main.asyncLoop.subTracker.reset()
    main.asyncLoop.innerTracker.reset()
    for task in main.asyncManager.children:
        task.tracker.reset()
        task.subTracker.reset()


def getStatusInfo(self:BasicServer, request:Request, tags:Optional[list[str]] = None) -> dict[str, Any]:
    main = self.main
    context = main.getContext()
    monitoredInfo = [ 
        #(i.name, inputSourceSnapshot(i)) for i in main._monitored
        (mv.source.name, inputSourceSnapshot(mv.source)) for mv in main.panel.monitored.values()
    ]

    monitored = dict( monitoredInfo  )
    rv:StrAnyDict =  {}

    def includeTag(tag: str) -> bool:
        if tags is None: return True
        return tag in tags

    def addTag(tag: str, val:Optional[Any]=None, **kwds:Any) -> None:
        if includeTag(tag):
            if val is not None:
                assert len(kwds) == 0, "Cannot pass both val and kwds to addTag"
            else:
                assert len(kwds) > 0, "Must pass either val or kwds to addTag"
                val = kwds
            rv[tag] = val
            
    
    addTag('supervisor', {
                'runtime': attrsToDict( supervisor.runtime, ['autoreload','run_reason'] ),
                'ticks_ms': supervisor.ticks_ms()
            } )
    addTag( 'microcontroller', 
           cpu = objectToDict(microcontroller.cpu)
    )
    
    if includeTag('gc'): rv['gc'] =  attrsToDict( gc, ['enabled','mem_alloc','mem_free'] )
    if includeTag('main'): rv['main'] = attrsToDict( main, ['cycle','when','newNow'],
                context = attrsToDict( context, ['updateIndex','when'] ),
                scenes = attrsToDict( main.scenes,["currentScenes"] ),
                # nextWait = main.asyncLoop.nextWait, # type: ignore
                nextRefresh  = main.asyncLoop.nextRefresh, # type: ignore
                priorWhen = main.asyncLoop.priorSleepWhen, # type: ignore
                #priorSleepDuration = main.__priorSleepDuration, # type: ignore
                latestSleepDuration = main.asyncLoop.latestSleepDuration # type: ignore
            )
    if includeTag('misc'): rv['misc'] ={
                'instanceCounts': CountedInstance._getCiInstanceCounts()
            }
    if includeTag('profiler'): rv['profiler'] = main.profiler.getProfilerInfo( dumpConfig=None )
    if includeTag('monitored'): rv['monitored'] = monitored
    if includeTag('asyncLoop'): rv['asyncLoop'] = getAsyncInfo(main)

    rv['request'] = {
        'path': request.path,
        'query_params': str(request.query_params),
    }

    return rv


@_BasicServer.reloadableMethod()
def BSR_sak(self:BasicServer, request:Request) -> JSONResponse | Response:
    """
    Serve a default static plain text message.
    """
    
    try:
        # Get objects
        if request.method == GET:
            
            return JSONResponse(request, getStatusInfo(self, request) )

        # Upload or update objects
        if request.method in {POST, PUT}:
            requestJson:StrAnyDict = request.json() # type:ignore[reportAttributeAccessIssue]
            assert requestJson is not None, "requestJson is None"
            result:StrAnyDict = {}
            if 'autoreload' in requestJson:
                autoreload:bool = requestJson['autoreload'] # type:ignore[reportAttributeAccessIssue]
                self.infoOut( "setting autoreload to %r", autoreload )
                supervisor.runtime.autoreload = autoreload
            if 'cmd' in requestJson:
                cmd = requestJson['cmd'] # type:ignore[reportAttributeAccessIssue]
                if cmd == 'resetTrackers':
                    resetTrackers(self.main)
                elif cmd == 'set':
                    settings:StrAnyDict = requestJson.get('settings', None) # type:ignore[reportAttributeAccessIssue]
                    assert isinstance(settings,dict)
                    
                    for tag, value in settings.items():
                        assert isinstance(tag, str), f"Expected tag to be a string, got {tag} ({type(tag)})"
                        if tag == 'loopMode':
                            assert isinstance(value, int), f"Expected loopMode to be an int, got {value} ({type(value)})"
                            self.main.asyncLoop.loopMode = value
                            resetTrackers(self.main)
                        else:
                            raise ValueError(f"Unknown setting tag: {tag}")

                else:
                    result['error'] = f"Unknown command: {cmd}"
            if requestJson.get('getStatusInfo',False):
                result.update( getStatusInfo(self, request) )
            return JSONResponse(request, result )

        else:
            self.errOut( "Unsupported request method %s", request.method )
            return JSONResponse(request, {"error": f"Unsupported request method {request.method}"}, status=405)
        return JSONResponse(request, getStatusInfo(self, request) )
    except Exception as inst:
        return ExceptionResponse(request, inst, "sak failed" )
    return JSONResponse(request, {"message": "Something went wrong"})


__sayBSR_sakRLImport.complete()
