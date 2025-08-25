from LumensalisCP.ImportProfiler import getImportProfiler
__profileImport = getImportProfiler( __name__, globals(), reloadable=True )

from LumensalisCP.HTTP.BSR.common import *

from LumensalisCP.Main import ManagerRL
from LumensalisCP.Main import Manager2RL
from LumensalisCP.Main import MainAsyncRL
from LumensalisCP.HTTP import BasicServerRL
from LumensalisCP.Temporal import RefreshableRL, RefreshableListRL
from LumensalisCP.Main import ProfilerRL
from LumensalisCP.HTTP.BSR import BSR_profileRL
from LumensalisCP.HTTP.BSR import BSR_sakRL
from LumensalisCP.HTTP.BSR import UIHelpers
from LumensalisCP.HTTP.BSR import BSR_cmdRL
from LumensalisCP.HTTP.BSR import BSR_clientRL
from LumensalisCP.HTTP.BSR import BSR_queryRL
from LumensalisCP.HTTP.BSR import BSR_proxyRL
from LumensalisCP.HTTP import WebsocketsRL

bsrReloadableModules:list[ModuleType] = [ 
    ManagerRL, Manager2RL, MainAsyncRL, 
    RefreshableRL, RefreshableListRL,
    ProfilerRL, BSR_profileRL, BSR_clientRL, UIHelpers, 
    BSR_cmdRL, BSR_queryRL, BSR_proxyRL, BSR_sakRL,
     BasicServerRL,WebsocketsRL,

       ]

def reloadablesForRoute(  self:BasicServer, name:str ) -> list[Any]:
    modules: list[Any] = [  ]
    from LumensalisCP.HTTP import BasicServerRL

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

    return modules

__all__ = [
    "reloadablesForRoute", "bsrReloadableModules"
]

__profileImport.complete(globals())

