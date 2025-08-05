from LumensalisCP.ImportProfiler import getImportProfiler
__sayBSR_cmdRLImport = getImportProfiler( globals(), reloadable=True )

from LumensalisCP.HTTP.BSR.common import *

from LumensalisCP.util.Reloadable import ReloadableModule

_module = ReloadableModule( 'LumensalisCP.HTTP.BasicServer' )
_BasicServer = _module.reloadableClassMeta('BasicServer')

from LumensalisCP.Main import ManagerRL
from LumensalisCP.Main import Manager2RL
from LumensalisCP.Main import MainAsyncRL
from LumensalisCP.HTTP import BasicServerRL
from LumensalisCP.Main import ProfilerRL
from LumensalisCP.HTTP.BSR import BSR_profileRL
from LumensalisCP.HTTP.BSR import BSR_clientRL
from LumensalisCP.HTTP.BSR import BSR_cmdRL
_reloadableModules:list[ModuleType] = [ ManagerRL, Manager2RL, MainAsyncRL, ProfilerRL, BSR_profileRL, BSR_clientRL, BasicServerRL, BSR_cmdRL ]

def _reloadAll(self:BasicServer ) -> list[Any]:

    for m in _reloadableModules:
        reload( m )
    #self.cvHelper = None
    return _reloadableModules

def _reload(self:BasicServer, module:str ) -> Any:
    for module in _reloadableModules:
        if module.__name__.endswith(module):
            reload( module )
            return module

    raise ValueError(f"Module {module} not found in reloadable modules.")

from LumensalisCP.Main.PreMainConfig import *

@_BasicServer.reloadableMethod()
def BSR_cmd(self:BasicServer, request:Request, cmd:Optional[str]=None, **kwds:StrAnyDict ) -> JSONResponse | Response:
    """
    """
    
    try:
        # Get objects
        print( f"BSR_cmd cmd={repr(cmd)} received...")
        assert isinstance(cmd,str)
        if cmd == "restart":
            def restart():
                print( "restarting" )
                supervisor.reload()
                
            self.main.callLater( restart )
            return JSONResponse(request, { "action":"restarting"} )
        
        if cmd == "reset":
            def reset():
                print( "resetting" )
                microcontroller.reset()
                
            self.main.callLater( reset )
            return JSONResponse(request, { "action":"resetting"} )

        if cmd == "toggleProfile":

            ep = not pmc_mainLoopControl.ENABLE_PROFILE
            pmc_mainLoopControl.ENABLE_PROFILE = ep
            self.main.profiler.disabled = ep
            return JSONResponse(request, { "ENABLE_PROFILE": ep })

        if cmd == "collect":
            rv = {
                "before": {
                    'mem_alloc': gc.mem_alloc(),
                    'mem_free': gc.mem_free(),
                }
            }

            pmc_gcManager.checkAndRunCollection( force=True, show=True )

            rv['after'] = {
                'mem_alloc': gc.mem_alloc(),
                'mem_free': gc.mem_free(),
            }
            return JSONResponse(request, rv)
        
        if cmd == "reloadAll":
            
            modules = _reloadAll(self)
            
            return JSONResponse(request, {
                    "action":"reloading",
                    "modules": [m.__name__ for m in modules]   # type:ignore[no-untyped-call]                    
                        } )
        
        if cmd.startswith("reload."):
            module = cmd[7:]
            m = _reload(self, module)
            return JSONResponse(request, {
                    "action":"reloading",
                    "module": m.__name__ if m else None
                        } )
        
        return JSONResponse(request, {"unknown command":cmd} )
    
    except Exception as inst:
        return ExceptionResponse(request, inst, "cmd failed" )
    
    return JSONResponse(request, {"message": "oops, command not handled..."})

__sayBSR_cmdRLImport.complete()