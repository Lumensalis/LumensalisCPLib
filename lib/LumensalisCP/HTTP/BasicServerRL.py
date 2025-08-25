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

from LumensalisCP.HTTP.BSR import bsrReloadables

@_BasicServer.reloadableMethod()
def _reloadForRoute( self:BasicServer, name:str ) -> None: # type:ignore[no-untyped-def]

    ImportProfiler.SHOW_IMPORTS = True
    ReloadableImportProfiler.SHOW_IMPORTS = True
    
    self.infoOut( "_reloadForRoute %s", name )
    pmc_gcManager.checkAndRunCollection(force=True)
    modules = bsrReloadables.reloadablesForRoute(self, name)

    self.infoOut( "reloading  %s", modules )
    
    for module in modules:
        reload( module )
    pmc_gcManager.checkAndRunCollection(force=True)
    self.infoOut( "_reloadForRoute %s complete", name )

__sayHTTPBasicServerRLImport.complete(globals())
