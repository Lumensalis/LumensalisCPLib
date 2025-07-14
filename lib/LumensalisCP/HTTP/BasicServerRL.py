
from . import BasicServer

import supervisor, gc, time

print( f"importing {__name__}..." )

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
                context = attrsToDict( context, ['updateIndex','when'] )
                )
            
        }
    return rv

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
        return JSONResponse(request, {"exception": repr(inst) } )
    return JSONResponse(request, {"message": "Something went wrong"})
    
    
def BSR_client(self:BasicServer.BasicServer, request: Request):
    
    print( f"get /client with {[v.name for v in self.monitoredVariables]}")
    vb = self.cvHelper.varBlocks(self.monitoredVariables)
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
    