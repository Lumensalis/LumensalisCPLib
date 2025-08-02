

from __future__ import annotations
import asyncio.lock  # type: ignore # pylint: disable=import-error,no-name-in-module

#############################################################################
from LumensalisCP.ImportProfiler import  getImportProfiler
_sayReleasableImport = getImportProfiler( "util.Releasable" )

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *

#############################################################################

class ReleasablePool(object):
    
    _freeHead:"Releasable|None"
    
    def __init__(self, cls:type ):
        self._freeHead = None
        self._allocs = 0
        self._releases = 0
        self._rIndex = 0
        self._cls = cls
        self._lock = asyncio.lock.Lock() # pylint: disable=no-member # type:ignore
    
    @property
    def cls(self) -> type:  
        return self._cls
    @property
    def allocs(self) -> int:
        return self._allocs 
    @property   
    def releases(self) -> int:
        return self._releases
    
class Releasable(object):
    """ Base for cacheable / reusable objects
    """
    # pylint: disable=protected-access
    # pyright: ignore[reportPrivateUsage]

    _inUse:bool
    _nextFree:Releasable|None
    _rIndex:int

    def __init__(self):
        self._inUse = False
        self._nextFree = None

    @classmethod 
    def getReleasablePool(cls) -> ReleasablePool:
        rv = getattr(cls,'__rp',None)
        if rv is None:
            rv = ReleasablePool(cls)
            setattr(cls,'__rp',rv)
        return rv
    
    @classmethod
    def releasablePreload(cls, count:int) -> None:
        rp = cls.getReleasablePool()
        count = max(0, count-rp.allocs)
        pmc_mainLoopControl.sayDebugAtStartup( "preloading %s[%d] with %d entries" % (cls.__name__, rp.allocs, count) )
        entries:list[Releasable|None] = [None]*count
        for i in range(count):
            entries[i] = cls() 

        pmc_mainLoopControl.sayDebugAtStartup( "releasing entries" )
        for entry in entries:
            assert entry._nextFree is None and not entry._inUse
            entry._releaseBase(rp)
        pmc_mainLoopControl.sayDebugAtStartup( "preloading complete" )

    @classmethod 
    def releasableGetInstance(cls) -> Self:
        rp = cls.getReleasablePool()
        entry = cls._make_getFree( rp )
        if entry is None:
            entry = cls()
        return entry # type: ignore
        
    @classmethod
    def _make_getFree(cls, rp:ReleasablePool) -> Self | None:
        if rp._freeHead is not None:  # pyright: ignore[reportPrivateUsage]
            entry = rp._freeHead # pyright: ignore[reportPrivateUsage]
            rp._freeHead = entry._nextFree # pyright: ignore[reportPrivateUsage]
            entry._nextFree = None
            return entry # type: ignore
        rp._allocs += 1 # pyright: ignore[reportPrivateUsage]
        return None            

    @classmethod
    def _makeFinish(cls, rp:ReleasablePool, entry:Self ) -> Self:
        assert entry._nextFree is None  and not entry._inUse
        entry._inUse = True
        entry._rIndex = rp._rIndex # pyright: ignore[reportPrivateUsage]
        rp._rIndex += 1 # pyright: ignore[reportPrivateUsage]
        return entry
                        

    @property
    def rindex(self) -> int:
        return self._rIndex
    
    def _releaseBase(self, rp: ReleasablePool) -> None:
        self._inUse = False
        self._nextFree = rp._freeHead # pyright: ignore[reportPrivateUsage]
        rp._freeHead = self # pyright: ignore[reportPrivateUsage]
        rp._releases += 1   # pyright: ignore[reportPrivateUsage]

    def release(self) -> None:
        assert self._inUse and self._nextFree is None
        rp = self.getReleasablePool()
        self._releaseBase(rp)
        try:
            self.releaseNested()
        except RuntimeError as e:
            pmc_mainLoopControl.sayDebugAtStartup(f"Error releasing nested resources: {e} in {self.__class__.__name__} @{id(self):X}") 
            raise


    def releaseNested(self):
        pass            

_sayReleasableImport.complete(globals())
