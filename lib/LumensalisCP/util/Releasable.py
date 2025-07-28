

from __future__ import annotations
import asyncio.lock  # type: ignore # pylint: disable=import-error,no-name-in-module

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *

class ReleasablePool(object):
    
    _freeHead:"Releasable|None"
    
    def __init__(self, cls ):
        self._freeHead = None
        self._allocs = 0
        self._releases = 0
        self._rIndex = 0
        self._cls = cls
        self._lock = asyncio.lock.Lock() # pylint: disable=no-member
    
class Releasable(object):
    """_summary_

    :param object: _description_
    :type object: _type_
    :return: _description_
    :rtype: _type_
    """
    # pylint: disable=protected-access
    
    @classmethod 
    def getReleasablePool(cls) -> ReleasablePool:
        rv = getattr(cls,'__rp',None)
        if rv is None:
            rv = ReleasablePool(cls)
            setattr(cls,'__rp',rv)
        return rv

    @classmethod 
    def releasableGetInstance(cls) -> Self:
        rp = cls.getReleasablePool()
        entry = cls._make_getFree( rp )
        if entry is None:
            entry = cls()
        return entry # type: ignore
        
    @classmethod
    def _make_getFree(cls, rp:ReleasablePool) -> Self | None:
        if rp._freeHead is not None:
            entry = rp._freeHead
            rp._freeHead = entry._nextFree
            entry._nextFree = None
            return entry # type: ignore
        rp._allocs += 1
        return None            

    @classmethod
    def _makeFinish(cls, rp:ReleasablePool, entry:Releasable ) -> Self:
        assert entry._nextFree is None  and not entry._inUse
        entry._inUse = True
        entry._rIndex = rp._rIndex
        rp._rIndex += 1
        return entry
                        
    _inUse:bool
    _nextFree:"Releasable|None"
    _rIndex:int
    @property
    def rindex(self) -> int:
        return self._rIndex
    
    def __init__(self):
        self._inUse = False
        self._nextFree = None
        
    def release(self):
        assert self._inUse and self._nextFree is None
        self._inUse = False
        rp = self.getReleasablePool()
        self._nextFree = rp._freeHead
        rp._freeHead = self
        rp._releases += 1
        self.releaseNested()

    def releaseNested(self):
        pass            
