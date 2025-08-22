from math import e
from LumensalisCP.ImportProfiler import getImportProfiler
__profileImport = getImportProfiler( __name__, globals(), reloadable=True  )

from LumensalisCP.HTTP.BSR.common import *

from LumensalisCP.util.Reloadable import ReloadableModule
from LumensalisCP.util.bags import Bag

_module = ReloadableModule( 'LumensalisCP.HTTP.BasicServer' )
_BasicServer = _module.reloadableClassMeta('BasicServer')

#############################################################################

class QueryConfig(Bag):
    recurse:int=1
    skipEmptyContainers:bool=True

    def __repr__(self)   -> str: 
        return repr(self.__dict__)


#############################################################################

def _proxyAddRecursive( config:QueryConfig, 
                        rv:StrAnyDict, 
                        target:NamedLocalIdentifiable|NliContainerInterface, 
                        recurse:int ) -> None:
    
    containers= [proxyData(config, c, recurse=recurse) for c in target.nliGetContainers() if len(c) or not config.skipEmptyContainers ]
    children= [proxyData(config, c, recurse=recurse) for c in target.nliGetChildren()]
    
    if target.isContainer():
        assert isinstance(target, NliContainerInterface), f"target {target.name} is not a NliContainerInterface, but {type(target)}"
        items = [proxyData(config, item, recurse=recurse) for item in target.values()] 
    else: items = []

    if recurse >= 0:
        if len(containers): rv["containers"] = containers
        if len(children): rv["children"] = children
        if len(items): rv["items"] = items
    else:
        rc:dict[str,int] = {}
        if len(containers): rc['containers'] = len(containers)
        if len(children): rc["children"] = len(children)
        if len(items): rc["items"] = len(items)
        if len(rc): rv["recurse"] = rc

#############################################################################
def proxyData( config:QueryConfig, target:NamedLocalIdentifiable|NliContainerInterface, recurse:int|None=None ) -> StrAnyDict:
    if isinstance(target,NamedLocalIdentifiable):
        return proxyNLIData( config, target, recurse=recurse )
    return proxyContainerData( config, target, recurse=recurse )

def proxyNLIData( config:QueryConfig, target:NamedLocalIdentifiable, recurse:int|None=None ) -> StrAnyDict:
    target.infoOut(f"proxyNLIData( %r, %r, %r )", target.name, type(target), recurse )
    rv:StrAnyDict = {
        "name": target.name,
        "type": type(target).__name__,
        "id": target.localId,
    }
    if recurse is None: recurse = config.recurse
    recurse -= 1
    if True:
        _proxyAddRecursive( config, rv, target, recurse=recurse )
    else:
        containers= [proxyData(config, c, recurse=recurse) for c in target.nliGetContainers()]
        children= [proxyData(config, c, recurse=recurse) for c in target.nliGetChildren()]
        
        if target.isContainer():
            assert isinstance(target, NliContainerInterface), f"target {target.name} is not a NliContainerInterface, but {type(target)}"
            items = [proxyData(config, item, recurse=recurse) for item in target.values()] 
        else: items = []

        if recurse >= 0:
            if len(containers): rv["containers"] = containers
            if len(children): rv["children"] = children
            if len(items): rv["items"] = items
        else:
            rc:dict[str,int] = {}
            if len(containers): rc['containers'] = len(containers)
            if len(children): rc["children"] = len(children)
            if len(items): rc["items"] = len(items)
            if len(rc): rv["recurse"] = rc

    return rv


def proxyContainerData( config:QueryConfig, target:NliContainerInterface, recurse:int|None=None ) -> StrAnyDict:
    target.infoOut(f"proxyContainerData( %r, %r, %r )", target.name, type(target), recurse )
    rv:StrAnyDict = {
        "name": target.name,
        "type": type(target).__name__,
        #"id": target.localId
    }
    if recurse is None: recurse = config.recurse
    recurse -= 1
    _proxyAddRecursive( config, rv, target, recurse=recurse )
    
    return rv

#############################################################################

def getProxyPath( config:QueryConfig, target:NamedLocalIdentifiable|NliContainerInterface, path:list[str], subPath:Optional[list[str]] = None , recurse:int|None=None ) -> Any: 
    if subPath is None: subPath = list(path)

    target.infoOut(f"getProxyPath( %r, %r, %r, %r )", target, path, subPath, recurse )
    if len(subPath):
        assert isinstance(target,NamedLocalIdentifiable)
        child = target.nliFind(subPath[0])
        if child is None: return { "missing child" : subPath[0]}
        #assert isinstance(child,NliContainerInterface), f"child {subPath[0]} is not a NliContainerMixinBaseMixin, but {type(child)}"

        return getProxyPath( config, child, path, subPath[1:], recurse=recurse  )

    if isinstance(target,NamedLocalIdentifiable):
        return proxyNLIData( config, target, recurse=recurse )
    return proxyContainerData( config, target, recurse=recurse )

@_BasicServer.reloadableMethod()
def BSR_proxy(self:BasicServer, request:Request, name:str):
    """
    """
    
    try:
        qc = QueryConfig(recurse=3)
        if request.method != 'GET':
            j = request.json()
            if j is not None:
                for tag,val in j.items(): # Process the JSON data
                    assert hasattr(qc, tag), f"unknown query config tag {tag}"
                    setattr(qc, tag, val)

        path:list[str] = [] if name == '.' else name.split('.')
        self.infoOut( f"querying path {path}" )
        rv = {
            "path": path,
            #"queryConfig": dict(qc),
            "recurse": qc.recurse,
            "result":  getProxyPath( qc, self.main, path, recurse=qc.recurse )
        }

        self.infoOut( f"result = %r", rv )

        return JSONResponse(request, rv )
    
    except Exception as inst:
        return ExceptionResponse(request, inst)
    return JSONResponse(request, {"message": "Something went wrong"})

__profileImport.complete()

