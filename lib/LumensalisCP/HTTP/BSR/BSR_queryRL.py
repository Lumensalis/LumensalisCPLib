from LumensalisCP.ImportProfiler import getImportProfiler
__profileImport = getImportProfiler( __name__, globals(), reloadable=True  )

from LumensalisCP.HTTP.BSR.common import *

from LumensalisCP.util.Reloadable import ReloadableModule

_module = ReloadableModule( 'LumensalisCP.HTTP.BasicServer' )
_BasicServer = _module.reloadableClassMeta('BasicServer')

#############################################################################
class QueryConfig(object):
    fillParents:bool = False
    recurseChildren:Optional[bool]=None
    includeName:bool = False
    includeId:bool = True
    includeType:bool = True

    def __repr__(self)   -> str: 
        return repr(self.__dict__)

def getQueryResult( target:NamedLocalIdentifiable|NliContainerInterface, path:list[str], qConfig:Optional[QueryConfig]=None ) -> Any: 
    rv = None
    if qConfig is None: qConfig=QueryConfig()
    target.infoOut(f"getQueryResult( %r, %r, %r )", target, path, qConfig) 
    if len(path):
        assert isinstance(target,NamedLocalIdentifiable)
        child = target.nliFind(path[0])
        if child is None: return { "missing child" : path[0]}
        #assert isinstance(child,NliContainerInterface), f"child {path[0]} is not a NliContainerMixinBaseMixin, but {type(child)}"
        if child.isContainer(): # isinstance(child,NliContainerInterface):
            assert isinstance(child,NliContainerInterface)
            rv = { child.containerName : getQueryResult( child, path[1:], qConfig )  }
            if not qConfig.fillParents: return rv
        else:
            rv = { child.name : getQueryResult( child, path[1:], qConfig )  }
            if not qConfig.fillParents: return rv
    else: 
        rv = {}
    name = getattr(target,"name",None)
    if qConfig.includeName and name is not None: rv['name'] = name
    if qConfig.includeType: # and not isinstance(target,NliContainerMixin):
        rv["type"] = type(target).__name__
    if qConfig.includeId and hasattr(target,'localId'): rv["localId"] = target.localId # type: ignore
    oldRecurseChildren = qConfig.recurseChildren
    if target.isContainer(): # isinstance(target,NliContainerInterface):
        rv['lenContainer'] = len(target)
        #rv['lenContainers'] = len(list(target.nliGetContainers()))
    try:
        if len(path) == 0 and qConfig.recurseChildren is None: qConfig.recurseChildren = True
        localRecurseChildren = qConfig.recurseChildren # and not len(path)
        containers = list(target.nliGetContainers() )#
        target.infoOut( f"querying containers {containers} with config {qConfig}" )
        if len( containers) > 0: 
            if localRecurseChildren:
                
                c:NliContainerInterface
                for c in containers:
                    cv = getQueryResult(c,[],qConfig=qConfig)
                    if len(cv): 
                        rv[c.name] = cv
            else:
                rv['containers'] = [(getQueryResult(c,[],qConfig=qConfig) if localRecurseChildren else c.name) for c in containers ]
                
        children = list( target.nliGetChildren())
        if len(children) > 0:
            if localRecurseChildren:
                for child in children:
                    v= getQueryResult(child,[],qConfig=qConfig)
                    #if len(v): 
                    rv[child.name] = v
            else:            
                rv['children'] = [(getQueryResult(child,[],qConfig=qConfig) if localRecurseChildren else child.name) for child in children ]
        if target.isContainer():
            assert isinstance(target,NliContainerInterface), f"target {target} is not a NliContainerInterface, but {type(target)}"                
            contained:list[Any] = []
            for child in target.values():
                contained.append(getQueryResult(child,[],qConfig=qConfig))
            rv['contained'] = contained
    except Exception as inst:
        rv['exception'] = {
            'message' : str(inst),
            'traceback' : traceback.format_exception(inst) ,
        }
        rv["kind"] = target.__class__.__name__ # type:ignore[reportUnknownMemberType]
    finally:
         qConfig.recurseChildren = oldRecurseChildren
         
    return rv        

@_BasicServer.reloadableMethod()
def BSR_query(self:BasicServer, request:Request, name:str):
    """
    """
    
    try:
        qc = QueryConfig()
        if request.method != 'GET':
            j:StrAnyDict|None = request.json()
            if j is not None:
                for tag,val in j.items(): # Process the JSON data
                    assert hasattr(qc, tag), f"unknown query config tag {tag}"
                    setattr(qc, tag, val)

        path:list[str] = [] if name == '.' else name.split('.')
        self.infoOut( f"querying path {path} with config {qc}" )
        result = getQueryResult( self.main, path, qConfig=qc )

        self.infoOut( f"result = %r", result )

        return JSONResponse(request, result )
    
    except Exception as inst:
        return ExceptionResponse(request, inst)
    return JSONResponse(request, {"message": "Something went wrong"})

__profileImport.complete()

