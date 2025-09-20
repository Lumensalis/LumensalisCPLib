from __future__ import annotations

from LumensalisCP.ImportProfiler import getImportProfiler
__importProfile = getImportProfiler( __name__, globals() )

from LumensalisCP.common import *
from LumensalisCP.Identity.Local import *
from LumensalisCP.Temporal.Refreshable import *
from collections import OrderedDict

if TYPE_CHECKING:
    from LumensalisCP.Main.Analyst import Analyst

#############################################################################

__importProfile.parsing()

# pyright: reportPrivateUsage=false

#############################################################################

def Analyst_preProxyRlForward(self:Analyst) -> None:
    if self._autoReload:
        self.infoOut("starting autoReload")
        self.rl()
        self.infoOut("finished autoReload")

def Analyst_afterReload(self:Analyst) -> None:
    # return analyzed_data
    pass

def Analyst_autoReload(self:Analyst, *args:Any, autoReload:Optional[bool]=True, 
                            **kwds:Any) -> Any:
    self.infoOut("autoReload(%r,%r, %r) called", args, autoReload, kwds )
    if autoReload is not None:
        self._autoReload = autoReload
    return self._autoReload

def Analyst_sak(self:Analyst, **kwds:Any) -> Any:
    # return analyzed_data
    return None

class QFilter(Debuggable):
    isaCache:ClassVar[dict[str,type]]  = {
        'Refreshable': Refreshable,
    }
    class KWDS(TypedDict):
        isa:NotRequired[str]
        hasItems:NotRequired[bool]

    def __init__( self, **kwds:Unpack[KWDS] ) -> None:
        super().__init__()
        self._filters:list[tuple[str, Callable[[NamedLocalIdentifiable,Any], bool]]] = []
        self._kwds = kwds

        def isaTest(nl:NamedLocalIdentifiable, v:str) -> bool:
            cls = QFilter.isaCache.get(v,None)
            assert cls is not None, f"Unknown class name for 'isa' filter: {v}"
            return isinstance(nl,cls)
        
        self._addFilter( 'isa', isaTest )
        self._addFilter( 'hasItems', lambda nl, v: nl.hasItems() )

    def _addFilter( self, tag:str, f:Callable[[NamedLocalIdentifiable,Any], bool] ) -> None:
        self._filters.append((tag, f))
        return
        val = self._kwds.get(tag, None)
        if val is not None:
            priorFilter = self._filter
            def newFilter(nl:NamedLocalIdentifiable) -> bool:
                return f(nl, val) or priorFilter(nl)
            self._filter = newFilter

    def _filter(self, nl:NamedLocalIdentifiable) -> bool:
        for tag, f in self._filters:
            val = self._kwds.get(tag, None)
            if val is not None:
                if f(nl, val):
                    #self.infoOut("QFilter _filter passed %s for %s", tag, nl.name )
                    return True
                #self.infoOut("QFilter _filter failed %s for %s", tag, nl.name )
                
        return False
    def __call__(self, nl:NamedLocalIdentifiable) -> bool:
        return self._filter(nl)

def Analyst_qsak(self:Analyst, 
            fItems:Optional[QFilter.KWDS]=None, 
            fChildren:Optional[QFilter.KWDS]=None, 
            **kwds:Any
    ) -> Any:
    rv:list[Any] = []

    
    qfItems = QFilter(**fItems) if fItems else None
    qfChildren = QFilter(**fChildren) if fChildren else None
    gnl = GetNamedLocalsArgs(fItems=qfItems, fChildren=qfChildren, **kwds)

    for nl in self.getNamedLocals(gnl=gnl):
        lid = nl.localId
        #assert lid not in rv, f"Duplicate localId found: {lid} for {nl.name}"
        #rv[lid] = nl.name
        if nl.isContainer():
            rv.append( ( f"{nl.__class__.__name__ }[{len(nl)}]",  nl.name, lid) )
        else:
            rv.append( ( nl.__class__.__name__, nl.name, lid ) )
    return rv

def Analyst_reportRefresh(self:Analyst, **kwds:Any) -> Any:
    gnl = GetNamedLocalsArgs(fItems=QFilter( isa='Refreshable'))
    rv:dict[int,dict[str,Any]] = {}

    for nl in self.getNamedLocals(gnl=gnl):
        assert isinstance(nl,Refreshable)
        if nl.localId in rv:
            self.warnOut( f"Duplicate localId found: {nl.localId} for {nl.name}")
            continue
        if nl.latestRefreshComplete is None:
            continue
        entry = OrderedDict()
        entry['name']=nl.name
        entry['localId']=nl.localId
        entry['kind']=nl.__class__.__name__
        entry['refreshCount']=nl.refreshCount
        entry['priorRefresh']=nl.priorRefresh
        entry['nextRefresh']=nl.nextRefresh
        entry['latestRefresh']=nl.latestRefresh
        entry['latestRefreshComplete']=nl.latestRefreshComplete
        entry['lastRefreshDuration']= (nl.latestRefreshComplete or 0) - (nl.latestRefresh or 0)
        if isinstance(nl,RfMxnPeriodic):
            refreshRate = getattr(nl,'__refreshRate', None)
            if callable(refreshRate):
                    entry['refreshRate'] = "()"
            else:
                entry['refreshRate'] = refreshRate

        if isinstance(nl,RfMxnActivatable):
            entry['active'] = nl.isActiveRefreshable


        refreshList = nl.refreshList
        if refreshList is not None:
            assert isinstance(refreshList, NamedLocalIdentifiable)

            entry['inRefreshList'] = dict(
                localId = refreshList.localId,
            )   
        rv[nl.localId] = entry
    return sorted(rv.items())


class GetNamedLocalsArgs:
    def __init__(self,
                fItems:Optional[QFilter]=None,
                fChildren:Optional[QFilter]=None,
                **kwds:Any 
            ):
        self.fItems = fItems
        self.fChildren = fChildren
        self.kwds = kwds

def Analyst_getNamedLocals(self:Analyst,
            root:Optional[NamedLocalIdentifiable]=None, 
            gnl:Optional[GetNamedLocalsArgs]=None,
            #fItems:Optional[QFilter]=None,
            #fChildren:Optional[QFilter]=None,
            #**kwds:Any
        ) -> Generator[NamedLocalIdentifiable]:
    if root is None:
        root = self.main
    assert gnl is not None
    if gnl.fItems is None:
        yield root
    elif gnl.fItems(root):
        #self.infoOut( f"getNamedLocals yielding {root.name} ({type(root)})")
        yield root

    if gnl.fChildren is None or gnl.fChildren._filter(root):
        for child in root.nliGetChildren():
            yield from self.getNamedLocals(child,  gnl=gnl)
        for container in root.nliGetContainers():
            yield from self.getNamedLocals(container, gnl=gnl)
        #if root.nliHasItems():
        ##    for item in root:
        #        yield from self.getNamedLocals(item, gnl=gnl)


#############################################################################

__importProfile.complete()
