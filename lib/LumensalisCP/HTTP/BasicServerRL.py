from LumensalisCP.ImportProfiler import getImportProfiler
__sayHTTPBasicServerRLImport = getImportProfiler( "HTTP.BasicServerRL", globals(), reloadable=True )

from LumensalisCP.ImportProfiler import ImportProfiler, ReloadableImportProfiler

from LumensalisCP.HTTP.BSR.common import *

from LumensalisCP.IOContext import *
from LumensalisCP.commonCPWifi import *
    
from LumensalisCP.util.Reloadable import ReloadableModule

#############################################################################
# pyright: ignore[reportUnusedImport]

#from LumensalisCP.HTTP.BSR.BSR_profileRL import BSR_profile 

_module = ReloadableModule( 'LumensalisCP.HTTP.BasicServer' )
_BasicServer = _module.reloadableClassMeta('BasicServer')

from LumensalisCP.Main import ProfilerRL
from LumensalisCP.HTTP.BSR import BSR_profileRL
from LumensalisCP.HTTP.BSR import BSR_sakRL
from LumensalisCP.HTTP.BSR import BSR_cmdRL
from LumensalisCP.HTTP.BSR import BSR_clientRL
from LumensalisCP.HTTP.BSR import BSR_queryRL
from LumensalisCP.HTTP.BSR import BSR_proxyRL
from LumensalisCP.HTTP import WebsocketsRL

@_BasicServer.reloadableMethod()
def _reloadForRoute( self:BasicServer, name:str ) -> None: # type:ignore[no-untyped-def]

    from LumensalisCP.HTTP import BasicServerRL
    modules: list[Any] = [  ]
    ImportProfiler.SHOW_IMPORTS = True
    ReloadableImportProfiler.SHOW_IMPORTS = True
    
    
    self.infoOut( "_reloadForRoute %s", name )
    pmc_gcManager.checkAndRunCollection(force=True)

    if "profile" in name:
        modules.extend( [ProfilerRL,  BSR_profileRL] )
    elif "sak" in name:
        modules.extend( [BSR_sakRL] )
    elif "cmd" in name:
        modules.extend( [BSR_cmdRL] )
    elif "client" in name:
        modules.extend( [BSR_clientRL] )
    elif "query" in name:
        modules.extend( [BSR_queryRL] )
    elif "proxy" in name:
        modules.extend( [BSR_proxyRL] )
    modules.append( BasicServerRL )

    self.infoOut( "reloading  %s", modules )
    
    for module in modules:
        reload( module )
    pmc_gcManager.checkAndRunCollection(force=True)
    self.infoOut( "_reloadForRoute %s complete", name )

__sayHTTPBasicServerRLImport.complete(globals())
