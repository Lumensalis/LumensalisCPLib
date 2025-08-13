from __future__ import annotations
from LumensalisCP.ImportProfiler import  getImportProfiler
__sayImport = getImportProfiler( __name__, globals() ) 

# pyright: reportUnusedImport=false, reportUnusedVariable=false

from collections import OrderedDict

from LumensalisCP.IOContext import *
from LumensalisCP.HTTP._httpBits import *
from LumensalisCP.pyCp.importlib import reload
from LumensalisCP.Main.PreMainConfig import pmc_gcManager, pmc_mainLoopControl
from LumensalisCP.util.Reloadable import ReloadableModule


if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
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

#############################################################################

class BSRRequest:
    requestJson:StrAnyDict

    def __init__(self, server:BasicServer, request:Request) -> None:
        self.server = server
        self.request = request
        self.result:StrAnyDict = {}
        if request.method in {POST, PUT}:
            self.requestJson = request.json() # type:ignore[reportAttributeAccessIssue]
            assert self.requestJson is not None, "requestJson is None"


        else:
            self.requestJson = {}

    def makeResponse(self):
        return JSONResponse(self.request, self.result )
    

#############################################################################


#############################################################################
RV = TypeVar('RV', )
class DecoratedActionGroup(Generic[RV],Debuggable):
     
    def __init__(self, name:str, prefix:str = "",description:str = "") -> None:
        Debuggable.__init__(self)
        self.name = name
        self._functions:dict[str, Callable[[BSRRequest], RV]] = {}
        self._prefix = prefix

    def __call__( self, name:Optional[str] = None ) -> Callable[[Callable[[BSRRequest], RV]], Callable[[BSRRequest], RV]]:
        def decorate( func:Callable[[BSRRequest], RV] ) -> Callable[[BSRRequest], RV]:
            if name is None:
                decoratedName = func.__name__
                assert isinstance(decoratedName, str), f"{self.name} handler name must be a string, got {name} ({type(name)})"
                assert decoratedName.startswith(self._prefix), f"Status topic name must start with {repr(self._prefix)}, got {name}"
                decoratedName = decoratedName[len(self._prefix):]  # remove prefix
            else:
                decoratedName = name

            self._functions[decoratedName] = func
            return func
        return decorate

    def matching( self, tag:str|list[str]|None ) -> Iterable[tuple[str,Callable[[BSRRequest],RV]] ]:  
        if tag is None:
            for fname, func in self._functions.items():
                yield (fname, func)
        elif isinstance(tag, str):
            func = self._functions.get(tag, None)
            assert func is not None, f"Unknown function {tag} in action group {self.name}"
            yield (tag, func)
        else: # tag is list[str]
            yield from [ (fname, func) for fname, func in self._functions.items() if fname in tag ]

    def gather( self, request:BSRRequest, tag:str|list[str]|None ) -> StrAnyDict:
        self.infoOut( "gathering %r for %r", tag, request.requestJson )
        rv:StrAnyDict = {}
        for fname, func in self.matching(tag):
            rv[fname] = func(request)

        return rv

    def actionNames(self):
        return list(self._functions.keys())

    def invoke(self, request:BSRRequest, funcName:Optional[str]=None, ) -> RV:
        if funcName is None:
            funcName = request.requestJson.get(self.name, None)
            assert isinstance(funcName,str)

        func = self._functions.get(funcName, None)
        if func is None:
            raise ValueError(f"Unknown function {funcName} in action group {self.name}")

        return func(request)

DecoratedActionGroupT = GenericT(DecoratedActionGroup)

#############################################################################

class QueryActionGroup(DecoratedActionGroupT[Union[StrAnyDict,List[Any]]]):
    pass

#############################################################################

__sayImport.complete(globals())