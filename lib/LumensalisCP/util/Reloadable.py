from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler
__sayImport = getImportProfiler( __name__, globals() )


from LumensalisCP.common import *

#############################################################################

ReloadableMethodType:TypeAlias = Callable[..., Any]

def __reloadPrint( message:str) -> None:
    #print( message )
    pass

class ReloadableModule(object):

    def __init__(self, name:Optional[str]=None, moduleGlobals:Optional[dict[str,Any]]=None):
        if name is None: 
            assert moduleGlobals is not None, "Either name or moduleGlobals must be provided."
            name = moduleGlobals.get('__name__' )
        self.name = name

    def reloadableClassMeta(self, name:str,  stripPrefix:Optional[str]=None) -> ReloadableClassMeta:
        name = f"{self.name}.{name}"
        rv = ReloadableClassMeta.make(name)
        rv.setModule(self)
        rv.addStripPrefix(stripPrefix)
        return rv


class ReloadableClassMeta(object):

    _metaDict:ClassVar[dict[str, ReloadableClassMeta]] = {}


    def __init__(self, name: str) -> None:
        __reloadPrint(f"Creating ReloadableClassMeta for {name}")
        self.name = name
        self.index = len(ReloadableClassMeta._metaDict)
        self._methods:dict[str, ReloadableMethodType] = {}
        self._cls:type|None = None
        self._stripPrefixList:list[str] = []
        self.module:Optional[ReloadableModule] = None
        assert name not in ReloadableClassMeta._metaDict, f"ReloadableClassMeta for {name} already exists."
        ReloadableClassMeta._metaDict[name] = self

    @staticmethod
    def make(name: str) -> ReloadableClassMeta:
        return ReloadableClassMeta._metaDict.get(name,None) or ReloadableClassMeta(name)
    
    def addStripPrefix(self, stripPrefix:Optional[str]) -> None:
        if stripPrefix is not None and stripPrefix not in self._stripPrefixList:
            self._stripPrefixList.append(stripPrefix)

    def __updateMethod(self, name:str, method: ReloadableMethodType) -> None:
        assert self._cls is not None, "Class has not been set."
        assert hasattr(self._cls, name), f"Class {self._cls} does not have method {name}.\n Available methods: {list(self._cls.__dict__.keys())}"
        __reloadPrint( f"replacing method {name} in {self._cls} with {method}" )
        setattr(self._cls, name, method)

    def setClass(self, cls: type) -> None:
        assert self._cls is None, "Class has already been set."
        __reloadPrint(f"Setting class {cls} for {self.name} ({len(self._methods)} methods)")
        self._cls = cls
        for method_name, method in self._methods.items():
            self.__updateMethod(method_name, method)
    def setModule(self, module: Optional[ReloadableModule]) -> None:
        if module is not None:
            self.module = module
            __reloadPrint(f"Setting module {module.name} for {self.name}")
        else:
            self.module = None

    def add_method(self, method_name: str, method: ReloadableMethodType) -> None:
        for prefix in self._stripPrefixList:
            if method_name.startswith(prefix):
                method_name = method_name[len(prefix):]
                break
        __reloadPrint(f"Adding reloadable method {method.__name__} to {self.name}.{method_name} {self}")
        self._methods[method_name] = method
        if self._cls is not None:
            self.__updateMethod(method_name, method)
    
    def __repr__(self) -> str:
        return f"ReloadableClassMeta({self.name}, {self.index}, {self._cls}, {self._methods.keys()})"
    
    def reloadableMethod(self, name:Optional[str]=None ) -> Callable[..., Callable[..., Any]]:
        def decorator( func:Callable[...,Any] ) -> Callable[...,Any]:
            #__reloadPrint(f"Adding reloadable method {func.__name__} to {self.name}")
            self.add_method(name or func.__name__, func)
            return func
        return decorator


def reloadableClassMeta(name:str, 
                        # module:Optional[ReloadableModule]=None, 
                        stripPrefix:Optional[str]=None) -> ReloadableClassMeta:

    rv = ReloadableClassMeta.make(name)
    #rv.setModule(module)
    rv.addStripPrefix(stripPrefix)
    return rv

def addReloadableClass(cls:type) -> type : # type: ignore
    assert isinstance(cls, type), f"Expected a class, got {cls}"
    name = f"{cls.__module__}.{cls.__name__}"
    meta = reloadableClassMeta(name)
    meta.setClass(cls)
    for method_name, method in cls.__dict__.items():
        assert not isinstance(method, ReloadingMethodStub), f"""Method {name}.{method_name} in {meta} has not been given a reloadable implementation ({
            ",\n   ".join( [ key + ":" + str(val.index) for key, val in ReloadableClassMeta._metaDict.items() ] )
            })."""
    return cls

def reloadableMethod( meta:ReloadableClassMeta, name:Optional[str]=None ) -> Callable[..., Callable[..., Any]]:
    def decorator( func:Callable[...,Any] ) -> Callable[...,Any]:
        #__reloadPrint(f"Adding reloadable method {func.__name__} to {meta.name}")
        meta.add_method(name or func.__name__, func)
        return func
    return decorator

class ReloadingMethodStub():
    def __init__(self,  func:Callable[...,Any] ) -> None:
        self.func = func

    def __call__(self, *args:Any, **kwargs:Any) -> Any:
        raise NotImplementedError(f"Method {self.func.__name__} is not implemented in the reloading context. Please use the reloadingMethod decorator to implement it.")

def reloadingMethod(func:Callable[...,Any] ) -> Callable[...,Any]:
    return ReloadingMethodStub(func)
    #__reloadPrint(f"Adding reloadable method {func.__name__} to {meta.name}")
    return func

#############################################################################

__sayImport.complete()
