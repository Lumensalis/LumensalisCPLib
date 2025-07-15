

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
import asyncio.lock


class ReleasablePool(object):
    
    _freeHead:"Releasable"
    
    def __init__(self, cls ):
        self._freeHead = None
        self._allocs = 0
        self._releases = 0
        self._rIndex = 0
        self._cls = cls
        self._lock = asyncio.lock.Lock()
    
class Releasable(object):
    """_summary_

    :param object: _description_
    :type object: _type_
    :return: _description_
    :rtype: _type_
    """
    
    @classmethod 
    def getReleasablePool(cls) -> ReleasablePool:
        rv = getattr(cls,'__rp',None)
        if rv is None:
            rv = ReleasablePool(cls)
            setattr(cls,'__rp',rv)

        return rv

    @classmethod
    def _make_getFree(cls, rp:ReleasablePool):
        if rp._freeHead:
            entry = rp._freeHead
            rp._freeHead = entry._nextFree
            entry._nextFree = None
            return entry
        rp._allocs += 1
        return None            

    @classmethod
    def _makeFinish(cls, rp:ReleasablePool, entry ):
        assert entry._nextFree is None  and not entry._inUse
        entry._inUse = True
        entry._rIndex = rp._rIndex
        rp._rIndex += 1
        return entry
                        
    @classmethod
    def __ddd__makeEntry(cls,*args, **kwds):
        rp = cls.getReleasablePool()
        entry = cls._make_getFree( rp )

        if entry is not None:
            entry.reset( *args, **kwds )
        else:
            entry = cls(*args, **kwds)

        cls._makeFinish( rp, entry )
            
        return entry

    _inUse:bool
    _nextFree:"Releasable"|None
    _rIndex:int
    
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
