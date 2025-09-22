from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler
__importProfile = getImportProfiler( __name__, globals() )

from LumensalisCP.common import *

from LumensalisCP.Identity.Local import *
from LumensalisCP.Main.Dependents import MainChild

from LumensalisCP.Identity.Proxy import proxyMethod, ProxyAccessibleClass
from LumensalisCP.pyCp.importlib import reload

from LumensalisCP.Main import AnalystRL

#############################################################################

@ProxyAccessibleClass()
class Analyst(MainChild):
    def __init__(self, **kwds:Unpack[MainChild.KWDS]) -> None:
        kwds.setdefault('name', 'Analyst')
        super().__init__(**kwds)
        self._autoReload:bool = False

    def _preProxyRlForward(self) -> None:
        AnalystRL.Analyst_preProxyRlForward(self)

    @proxyMethod()
    def rl(self) -> None:
        # Perform analysis on the data
        reload(AnalystRL)
        AnalystRL.Analyst_afterReload(self)

    @proxyMethod()
    def autoReload(self,*args:Any, **kwds:Any ) -> None:
        self._preProxyRlForward()
        return AnalystRL.Analyst_autoReload(self, *args, **kwds)
    
    @proxyMethod()
    def sak(self,**kwds:Any ) -> None:
        self._preProxyRlForward()
        return AnalystRL.Analyst_sak(self, **kwds)

    @proxyMethod()
    def qsak(self,**kwds:Any ) -> None:
        self._preProxyRlForward()
        return AnalystRL.Analyst_qsak(self, **kwds)

    def getNamedLocals(self, root:Optional[NliInterface]=None, **kwds:Any) -> Generator[NamedLocalIdentifiable]:
        return AnalystRL.Analyst_getNamedLocals(self, root=root, **kwds)

    @proxyMethod()
    def reportRefresh(self,**kwds:Any ) -> None:
        self._preProxyRlForward()
        return AnalystRL.Analyst_reportRefresh(self, **kwds)

#############################################################################

__importProfile.complete()
