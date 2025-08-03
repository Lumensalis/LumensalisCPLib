from LumensalisCP.ImportProfiler import getImportProfiler
__sayBSR_sakRLImport = getImportProfiler( globals(), reloadable=True )

from LumensalisCP.HTTP.BSR.common import *

#from LumensalisCP.Main.Async import AsyncLoop

def getAsyncInfo(main:MainManager) -> dict[str, Any]:
    asyncLoop = main.asyncLoop
    asyncManager = main.asyncManager

    children = dict( [(getattr(task,'name',None) or task.dbgName, task.asyncTaskStats()) for task in  asyncManager.children] ) 

    return {


        'nextWait': asyncLoop.nextWait,
        'nextRefresh': asyncLoop.nextRefresh,
        'priorWhen': asyncLoop.priorSleepWhen,
        'latestSleepDuration': asyncLoop.latestSleepDuration,
        'children' : children,
    }

def getStatusInfo(self:BasicServer, request:Request ) -> dict[str, Any]:
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
                nextWait = main.asyncLoop.nextWait, # type: ignore
                nextRefresh  = main.asyncLoop.nextRefresh, # type: ignore
                priorWhen = main.asyncLoop.priorSleepWhen, # type: ignore
                #priorSleepDuration = main.__priorSleepDuration, # type: ignore
                latestSleepDuration = main.asyncLoop.latestSleepDuration # type: ignore
            ),
            'monitored': monitored,
            'asyncLoop': getAsyncInfo(main)
        }
    return rv


def BSR_sak(self:BasicServer, request:Request):
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


__sayBSR_sakRLImport.complete()
