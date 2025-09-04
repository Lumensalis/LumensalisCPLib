""" Support for adding "proxy" behavior to classes, accessible for remote method invocation.

This allows classes to expose specific methods for "remote access".  Currently,
that takes the form of REST calls through /proxy route, but this will likely
expand to other forms of remote invocation in the future.


"""

from __future__ import annotations



from LumensalisCP.ImportProfiler import  getImportProfiler
__profileImport = getImportProfiler( __name__, globals() )

# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

from LumensalisCP.common import *
from LumensalisCP.Debug import Debuggable
import LumensalisCP.pyCp.weakref as lcpWeakref
from LumensalisCP.CPTyping import ReferenceType, Optional, Iterable , Generic, TypeVar, GenericT
from LumensalisCP.pyCp.collections import GenericList, GenericListT
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
#############################################################################

#############################################################################

__profileImport.parsing()

P = ParamSpec('P')
T = TypeVar('T')
R = TypeVar('R')
_NLIPA_SELF_T=TypeVar('_NLIPA_SELF_T', bound=NamedLocalIdentifiable)

class NamedLocalInstanceProxyAction(Generic[_NLIPA_SELF_T,P,R]):

    def __init__(self, 
                   name:str,
                   action:Callable[Concatenate[_NLIPA_SELF_T,P], R]
                ) -> None:
        self.name:str = name
        self.action = action
        self.__wrapperName = f"__proxy_{name}"

    def __get__(self, instance:_NLIPA_SELF_T, owner:Any=None) -> Callable[P,R]:
        wrapped:Callable[P,R]|None = getattr(instance, self.__wrapperName, None)
        if wrapped is None:
            def wrapper(*args:Any, **kwds:Any) -> Any:
                return self.action(instance, *args, **kwds)
            wrapped = wrapper
            setattr(instance, self.__wrapperName, wrapper)
        return wrapped

    def __set__(self, instance:_NLIPA_SELF_T, value:Any) -> None:
        raise NotImplementedError( f"Cannot set {self.name} ")   

NamedLocalInstanceProxyActionT = GenericT(NamedLocalInstanceProxyAction)


#class GenericNamedLocalInstanceProxyAction(NamedLocalInstanceProxyActionT[NamedLocalIdentifiable,Any,Any]):
#    pass
if TYPE_CHECKING:
    GenericNamedLocalInstanceProxyAction:TypeAlias = NamedLocalInstanceProxyAction[NamedLocalIdentifiable,Any,Any]
else:    
    GenericNamedLocalInstanceProxyAction:TypeAlias = NamedLocalInstanceProxyActionT[NamedLocalIdentifiable,Any,Any]

#############################################################################
class AddProxyAccessibleClassKWDS(TypedDict): 
    modules: NotRequired[Any]
    checkMethods: NotRequired[bool]

def addProxyAccessibleClass(cls:type, **kwds:Unpack[AddProxyAccessibleClassKWDS]) -> type : # type: ignore

    assert isinstance(cls, type), f"Expected a class, got {cls}"
    name = f"{cls.__module__}.{cls.__name__}"
    proxyActions:dict[str, GenericNamedLocalInstanceProxyAction] = {}
    #print(f"Adding proxy accessible class: {name}")
    assert getattr(cls,'_clsProxyActions',None) is None, f"Class {name} already has _clsProxyActions"
    cls._clsProxyActions = proxyActions
    #for val in cls.__dict__.values():
    for tag in dir(cls):
        val = getattr(cls, tag, None)
        if isinstance(val, NamedLocalInstanceProxyAction):
            proxyActions[tag] = val
            # print(f"Adding proxy action {val.name} to {name}")
    return cls

_CLASS_T = TypeVar("_CLASS_T", bound=type)
class ProxyAccessibleClass:
    """ Decorator to mark a class as proxy accessible.
    
    This allows the LCPF to automatically detect and register any class
    methods marked with `@proxyMethod(...)`.  
    
    Proxy marking is class specific, i.e.
    it only applies to direct methods of the class being decorated,
    _not_ methods inherited from parent classes or defined in child classes.
    
    If a class defines it's own `@proxyMethod()`s and derives from a parent 
    class which _also_ defines it's own `@proxyMethod()`s,  decorating _both_
    classes with `@ProxyAccessibleClass()` is not only acceptable but required in order to make all
    of the proxy methods remotely accessible.  (normally this could be more 
    easily achieved using python metaclasses, but those are not
    supported in CircuitPython )

    """
    def __init__(self,  **kwds:Unpack[AddProxyAccessibleClassKWDS]) -> None:
        self.kwds = kwds

    def __call__(self, cls:_CLASS_T) -> _CLASS_T:
        # This method is called with the class being decorated
        addProxyAccessibleClass(cls, **self.kwds)
        return cls
    
#############################################################################

def proxyMethod(  
                ) -> Callable[ [ Callable[Concatenate[_NLIPA_SELF_T,P], R] ],
            NamedLocalInstanceProxyAction[_NLIPA_SELF_T,P,R] ]:
    """Decorator to mark a method as a proxy method.

    Methods marked with `@proxyMethod(...)`  *_in a class marked with 
    `@ProxyAccessibleClass()`_* will be automatically registered by
    the LCPF to be available for remote invocation.

    """
    
    def decorated(method:Callable[Concatenate[_NLIPA_SELF_T,P], R]  ):
        rv = NamedLocalInstanceProxyAction(
                    name=method.__name__,
                    action=method
                )
        cls = getattr(method,'__class__',None)
        if cls is None:
            print( f"\n#####\nWARNING: proxyMethod {method} has no class\n#####\n")
        else:
            clsName = cls.__name__
            if clsName == 'function':
                #print( f"\n#####\nWARNING: proxyMethod {method} no class in {dir(cls)} / {getattr(cls, '__dict__', {})}\n#####\n")
                pass
            else:
                print( f"\n#####\nHOORAH!proxyMethod {method} registering for {cls.__name__} in {dir(cls)}\n#####\n")
                clsDescriptors:dict[str,GenericNamedLocalInstanceProxyAction]|None = NamedLocalIdentifiable._proxyActions.get(clsName, None)
                if clsDescriptors is None:
                    clsDescriptors = {}
                    NamedLocalIdentifiable._proxyActions[clsName] = clsDescriptors
                clsDescriptors[rv.name] = rv
        return rv
    return decorated    

proxyMethodT = GenericT(proxyMethod)

#############################################################################

__all__ = ['proxyMethod', 'ProxyAccessibleClass', 'GenericNamedLocalInstanceProxyAction'
           ]
__profileImport.complete(globals())
