from __future__ import annotations
from LumensalisCP.ImportProfiler import  getImportProfiler
__sayImport = getImportProfiler( __name__, globals() ) 

# pyright: reportUnusedImport=false, reportUnusedVariable=false

from collections import OrderedDict

from LumensalisCP.IOContext import *
from LumensalisCP.HTTP._httpBits import *
from LumensalisCP.pyCp.importlib import reload
from LumensalisCP.Main.PreMainConfig import pmc_gcManager, pmc_mainLoopControl

if TYPE_CHECKING:
    from LumensalisCP.HTTP.BasicServer import BasicServer


__sayImport.parsing()

v2jSimpleTypes:set[type] = { int, str, bool, float,type(None) }

def valToJson( val:Any ) -> Any:
    if type(val) in v2jSimpleTypes: return val
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


__sayImport.complete(globals())