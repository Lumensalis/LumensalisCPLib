from LumensalisCP.ImportProfiler import getImportProfiler
__profileImport = getImportProfiler( __name__, globals(), reloadable=True  )

from LumensalisCP.HTTP.BSR.common import *

from LumensalisCP.util.Reloadable import ReloadableModule
from LumensalisCP.util.bags import Bag
from LumensalisCP.util.ObjToDict import objectToDict, objectToVal
_module = ReloadableModule( 'LumensalisCP.HTTP.BasicServer' )
_BasicServer = _module.reloadableClassMeta('BasicServer')

#############################################################################

class ProxyRequestConfig(Bag):
    recurse:int=1
    skipEmptyContainers:bool=True
    path:list[str]|None = None
    localId:int|None = None
    cmd:str|None = None
    setting:str|None = None
    setValue:Any = None
    debug:bool = False
    includeInherited:bool = False
    includePrivate:bool = False

    def __repr__(self)   -> str: 
        return repr(self.__dict__)

#############################################################################

def _count( i:Iterable[Any]|None, filter:Optional[Callable[[Any], bool]]=None ) -> int:
    if i is None: return 0
    if hasattr(i,'__len__') and filter is None: return len(i) # type: ignore
    c = 0
    for _ in i:
        if filter is not None:
            if not filter(_): continue
        c += 1
    return c

def _proxyAddRecursive( config:ProxyRequestConfig, 
                        rv:StrAnyDict, 
                        target:NamedLocalIdentifiable|NliContainerInterface, 
                        recurse:int ) -> None:

    if recurse >= 0:
        containers= [proxyData(config, c, recurse=recurse) for c in target.nliGetContainers() if _count(c.values())>0 or not config.skipEmptyContainers ]
        targetChildren = target.nliGetChildren()
        children= [proxyData(config, c, recurse=recurse) for c in targetChildren ] if targetChildren is not None else []
        
        if target.isContainer():
            assert isinstance(target, NliContainerInterface), f"target {target.name} is not a NliContainerInterface, but {type(target)}"
            items = [proxyData(config, item, recurse=recurse) for item in target.values()] 
        else: items = []
        if len(containers): rv["containers"] = containers
        if len(children): rv["children"] = children
        if len(items): rv["items"] = items
    else:
        rc:dict[str,int] = {}
        if target.nliHasContainers():
            if (containers:= _count( target.nliGetContainers(), lambda c:  len(c) > 0 or not config.skipEmptyContainers )) > 0:
                rc['containers'] = containers
        if target.nliHasChildren():
            if (children:= _count( target.nliGetChildren() )): rc["children"] = children
        if target.nliHasItems():
            assert isinstance(target, NliContainerInterface), f"target {target.name} is not a NliContainerInterface, but {type(target)}"
            if items := _count( target.values() ): rc["items"] = items

        if len(rc): rv["recurse"] = rc

#############################################################################
def proxyData( config:ProxyRequestConfig, target:NamedLocalIdentifiable|NliContainerInterface, recurse:int|None=None ) -> StrAnyDict:
    if isinstance(target,NamedLocalIdentifiable):
        return proxyNLIData( config, target, recurse=recurse )
    return proxyContainerData( config, target, recurse=recurse )

def proxyNLIData( config:ProxyRequestConfig, target:NamedLocalIdentifiable, recurse:int|None=None ) -> StrAnyDict:
    if config['debug']: target.infoOut(f"proxyNLIData( %r, %r, %r )", target.name, type(target), recurse )
    rv:StrAnyDict = {
        "name": target.name,
        "type": type(target).__name__,
        "localId": target.localId,
    }
    if target.enableDbgOut:
        rv['enableDbgOut'] = target.enableDbgOut
    if isinstance(target, Tunable ):
        if config['debug']: target.infoOut(f"proxyNLIData( %r ) %s is a Tunable", target.name, type(target) )
    
        rv['settings'] = _tune(config,target)
    if recurse is None: recurse = config.recurse
    recurse -= 1
    _proxyAddRecursive( config, rv, target, recurse=recurse )
    
    return rv

def proxyContainerData( config:ProxyRequestConfig, target:NliContainerInterface, recurse:int|None=None ) -> StrAnyDict:
    if config['debug']: target.infoOut(f"proxyContainerData( %r, %r, %r )", target.name, type(target), recurse )
    rv:StrAnyDict = {
        "name": target.name,
        "type": type(target).__name__,
        "localId": getattr(target, "localId", None)
    }
    if target.enableDbgOut:
        rv['enableDbgOut'] = target.enableDbgOut

    if recurse is None: recurse = config.recurse
    recurse -= 1
    _proxyAddRecursive( config, rv, target, recurse=recurse )
    
    return rv

#############################################################################

def getProxyTargetByPath( target:NamedLocalIdentifiable|NliContainerInterface, 
        path:list[str], subPath:Optional[list[str]] = None 
        ) -> NamedLocalIdentifiable|NliContainerInterface|None: 
    if subPath is None: subPath = list(path)

    #if config['debug']: target.infoOut(f"getProxyTargetByPath( %r, %r, %r )", target, path, subPath )
    if len(subPath):
        assert isinstance(target,NamedLocalIdentifiable)
        child = target.nliFind(subPath[0])
        if child is None: return None
        #assert isinstance(child,NliContainerInterface), f"child {subPath[0]} is not a NliContainerMixinBaseMixin, but {type(child)}"

        return getProxyTargetByPath( child, path, subPath[1:] )
    return target

def getProxyPath( config:ProxyRequestConfig, 
                 base:NamedLocalIdentifiable|NliContainerInterface, path:list[str], 
                 subPath:Optional[list[str]] = None , recurse:int|None=None ) -> Any: 
    if subPath is None: subPath = list(path)

    if config['debug']: base.infoOut(f"getProxyPath( %r, %r, %r, %r )", base, path, subPath, recurse )
    target = getProxyTargetByPath( base, path, subPath )
    if target is None:
        return { "missing child" : path}

    if isinstance(target,NamedLocalIdentifiable):
        return proxyNLIData( config, target, recurse=recurse )
    return proxyContainerData( config, target, recurse=recurse )

#############################################################################

def getProxyTarget( base:Optional[NamedLocalIdentifiable|NliContainerInterface]=None, 
        path:Optional[str|list[str]]=None, localId:Optional[int]=None
        ) -> NamedLocalIdentifiable|NliContainerInterface|None: 
    
    if localId is not None:
        #assert path is None, f"localId is set but path is {path}"
        #assert base is None, f"base is set but localId is {localId}"
        return LocalIdentifiable.localsMap.get(localId, None) # type: ignore

    if base is None: base = getMainManager()
    assert path is not None
    if len(path) == 0: return base 

    if isinstance(path,str):
        if path == "": return base
        path = path.split('.')
    if len(path) == 0: return base         
    if len(path) == 1 and path[0] == "": return base
    
    return getProxyTargetByPath( base, path )

#############################################################################

def _inspectClass( config:ProxyRequestConfig, cls:type, recurse:bool=False ) -> StrAnyDict:
    rv = { "name": cls.__name__ }
    bases = [b for b in cls.__bases__ if b is not object]
    if len(bases): rv["bases"] = [ _inspectClass(config, b, recurse=recurse) if recurse else b.__name__ for b in  bases ]

    return rv

def _inspectDir( config:ProxyRequestConfig, target:NamedLocalIdentifiable|NliContainerInterface ) :
    rv:  dict[str, list[str]] = { }
    attrs:list[str]  = []
    callables:list[str] = []
    properties:list[str]  = []
    methods:list[str]  = []
    cls = target.__class__
    d = target.__dict__

    for v in  dir(cls) if config.includeInherited else cls.__dict__:
        if v in d: continue
        if v.startswith('_') and not config.includePrivate: continue
        if callable(getattr(cls, v)) and not v.startswith('_'):
            methods.append(v)
        elif isinstance(getattr(cls, v), property):
            properties.append(v)
        #elif not v.startswith('_'):
        #    attrs.append(v)
    for tag,val in d.items():
        if tag.startswith('_') and not config.includePrivate: continue
        if callable(val):
            callables.append(tag)
        else:
            attrs.append(tag)

    if len(attrs): rv['attrs'] = attrs
    if len(callables): rv['callables'] = callables
    if len(properties): rv['properties'] = properties
    if len(methods): rv['methods'] = methods
    return rv

def _inspect(  config:ProxyRequestConfig, target:NamedLocalIdentifiable|NliContainerInterface ) -> dict[str, Any]:
    rv: dict[str, Any] = {
        'name': target.name,
        'localId': target.localId,
        'module': target.__class__.__module__,
        'class': _inspectClass(config, target.__class__),
        'dir': _inspectDir(config, target)
    }

    return rv

#############################################################################

def _tune(  config:ProxyRequestConfig, target:Tunable ) -> dict[str, Any]:

    if config.setting is not None and config.setValue is not None:
        #target.tune( config.setting, config.setValue )
        raise NotImplementedError("tuning via proxy not implemented yet")
    else:
        rv: dict[str, Any] = {
            'active': [{'name': setting.name, 
                        'value': setting.value, 
                        'cls': setting.__class__.__name__, 
                        'spec': setting.interactSpec()
                    } for setting in target.activeSettings()],
            'inactive': [{
                    'name': descriptor.name, 
                    'cls': descriptor.settingClass.__name__, 
                    'default': descriptor.default,
                    'kwds': objectToVal(descriptor._settingKwds),
                } for descriptor in target.inactiveSettings()]
        }
        

    return rv


#############################################################################

@_BasicServer.reloadableMethod()
def BSR_proxy(self:BasicServer, request:Request, name:Optional[str]=None):
    """
    """
    
    try:
        assert request.method != 'GET'
        qc = ProxyRequestConfig(recurse=3)
        j:StrAnyDict = request.json() # type.ignore
        for tag,val in j.items(): # Process the JSON data
            assert hasattr(qc, tag), f"unknown query config tag {tag}"
            if tag == "path":
                if isinstance(val, str):
                    val = val.split('.')
                elif val is None: val = []
            setattr(qc, tag, val)
        if name is not None and len(name) > 1:
            qc.path  = name.split('.')
        self.infoOut( f"BSR_proxy path={qc.path!r} localId={qc.localId} cmd={qc.cmd}" )

        #assert isinstance(qc.path, list), f"qc.path should be a list, but is {type(qc.path)}"
        target = getProxyTarget( base=self.main, path=qc.path, localId=qc.localId )
    
        rv:StrAnyDict = {
            'session':self.main.sessionUuid,
            'error':None,
            "path": qc.path,
            "queryConfig": qc.asDict(),
        }
        if target is None:
            rv['error'] = f"Target not found for path {qc.path} / localId {qc.localId}"
        elif qc.cmd =="query":
            rv.update({
                "path": qc.path,
                "queryConfig": qc.asDict(),
                "recurse": qc.recurse,
                "result":  proxyData( qc, target )
            })

        elif qc.cmd =="inspect":
            rv['inspect'] = _inspect(qc,target)
        elif qc.cmd =="tune":
            assert isinstance(target, Tunable), f"Target {target} is not Tunable, but {type(target)}"
            rv['tune'] = _tune(qc,target)
        elif qc.cmd == "enableDbgOut":
            if qc.setValue is not None:
                target.enableDbgOut = bool(qc.setValue)
            rv['enableDbgOut'] = target.enableDbgOut
        else:
            rv['error'] =  f"Unknown command {qc.cmd!r} in {qc}"

        self.infoOut( f"result = %r", rv )

        return JSONResponse(request, rv )
    
    except Exception as inst:
        self.SHOW_EXCEPTION(inst,"error handling proxy command")
        return JSONResponse( request,
            { 
                'session': self.main.sessionUuid,
                'exception' : str(inst),
                #'message': message or f"unhandled exception",
                'traceback' : traceback.format_exception(inst) 
            }
        )

__profileImport.complete()

