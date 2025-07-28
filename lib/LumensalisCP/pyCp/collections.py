from __future__ import annotations

from LumensalisCP.Main.PreMainConfig import ImportProfiler
_saypyCpcollectionsImport = ImportProfiler( "pyCp.Collections" )


try:
    from collections import * # pylint: disable=unused-wildcard-import # type: ignore
except ImportError:
    pass

from LumensalisCP.CPTyping import Generic,TypeVar,Optional, GenericT, Any, TYPE_CHECKING # pyright: ignore[unused-import] # type: ignore

_ULT = TypeVar('_ULT',)

class GenericList(Generic[_ULT]): # type:  ignore # pylint: disable=function-redefined
    """A minimally complete user-defined wrapper around list objects."""

    def __init__(self, initList:Optional[list[_ULT]|GenericList[_ULT]]=None):
        self.data:list[_ULT] = []
        if initList is not None:
            # XXX should this accept an arbitrary sequence?
            #if type(initList) == type(self.data):
            if isinstance(initList, list):
                self.data[:] = initList
            elif isinstance(initList, GenericList):
                self.data[:] = initList.data[:]
            else:
                self.data = list(initList)

    def __repr__(self):
        return repr(self.data)

    def __contains__(self, item:_ULT) -> bool:
        return item in self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i:int) -> _ULT:
        #if isinstance(i, slice):
        #    return self.data[i]
        #else:
        return self.data[i]

    def __setitem__(self, i:int, item:_ULT) -> None:
        self.data[i] = item

    def __delitem__(self, i:int) -> None:
        del self.data[i]

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["data"] = self.__dict__["data"][:]
        return inst

    def append(self, item:_ULT) -> None:
        self.data.append(item)


    def remove(self, item:_ULT) -> None:
        self.data.remove(item)

    def clear(self) -> None:
        self.data.clear()


GenericListT = GenericT(GenericList)


_saypyCpcollectionsImport.complete()
