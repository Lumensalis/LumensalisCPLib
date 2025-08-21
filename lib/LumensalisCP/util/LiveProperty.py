from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( __name__, globals() )

from LumensalisCP.common import *

#############################################################################

class LivePropertyHolder:
    def onDescriptorSet(self, name:str, value:Any) -> Any:
        """Called when a descriptor is set on this object"""
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement onDescriptorSet")
        
_LPT = TypeVar('_LPT' )
_LCT = TypeVar('_LCT',contravariant=True )

#############################################################################

class LivePropertyDescriptor(Generic[_LCT,_LPT]):
    def __init__(self, name:str, default:_LPT|None = None):
        self.name = name
        self.attrName = f"_d_{name}"
        self.default = default

    def __get__(self, instance:_LCT, owner:Any=None) -> _LPT:
        rv = getattr( instance, self.attrName,None )
        if rv is None: rv = self.default
        return rv # type: ignore
    
    def _reportSet(self, instance:_LCT, value:_LPT) -> None:
        instance.onDescriptorSet(self.name, value)

    def __set__(self, instance:_LCT, value:_LPT) -> None:
        assert instance is not None,  f"Cannot set {self.name} "
        setattr( instance, self.attrName, value )
        self._reportSet(instance, value)

#############################################################################
if TYPE_CHECKING:

    class LiveWrappedPropertyWrapper(Protocol[_LCT,_LPT]):
        pass
        def __init__(self, instance:_LCT, name:str, default:_LPT|None = None, owner:Any = None, **kwds:Any) -> None: ...

        def get(self,name:str, instance:_LCT)-> _LPT: raise NotImplementedError
        def set(self,name:str, instance:_LCT, value:_LPT) -> None: raise NotImplementedError

else:
    class LiveWrappedPropertyWrapper(Generic[_LCT,_LPT]): ...

class LiveWrappedPropertyDescriptor(Generic[_LCT,_LPT]):
    def __init__(self,
                wrapper:Type[LiveWrappedPropertyWrapper[_LCT,_LPT]],
                name:str, default:Optional[_LPT] = None, **kwds:Any
            ) -> None:
        self.name = name
        self.wrapperClass:Type[LiveWrappedPropertyWrapper[_LCT,_LPT]] = wrapper
        #self.attrName = f"_d_{name}"
        self.wrapperName = f"_pw_{name}"
        self.default = default
        self.kwds = kwds

    def __addWrapper(self, instance:_LCT, owner:Any=None
                     ) -> LiveWrappedPropertyWrapper[_LCT,_LPT] :
        assert getattr(instance, self.wrapperName, None) is None
        wrapper = self.wrapperClass( instance=instance, 
                name=self.name, default=self.default, owner=owner, **self.kwds )
        setattr(instance, self.wrapperName, wrapper)
        return wrapper

    def __get__(self, instance:_LCT, owner:Any=None) -> _LPT:
        wrapper = getattr( instance, self.wrapperName,None ) or self.__addWrapper(instance,  owner=owner)
        return wrapper.get(self.name, instance) # type: ignore

    def __set__(self, instance:_LCT, value:_LPT, owner:Any=None) -> None:
        wrapper = getattr( instance, self.wrapperName,None ) or self.__addWrapper(instance,  owner=owner)
        wrapper.set(self.name, instance, value) # type: ignore

#############################################################################


__all__ = [
    'LivePropertyDescriptor',
    'LiveWrappedPropertyDescriptor',
    'LiveWrappedPropertyWrapper',
    'LivePropertyHolder',

]

_sayImport.complete()
