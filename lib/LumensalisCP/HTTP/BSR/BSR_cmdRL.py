from LumensalisCP.ImportProfiler import getImportProfiler
__sayBSR_cmdRLImport = getImportProfiler( globals(), reloadable=True )

from LumensalisCP.HTTP.BSR.common import *

def _reloadAll(self:BasicServer ):
    from LumensalisCP.Main import ManagerRL
    from LumensalisCP.HTTP import BasicServerRL
    from LumensalisCP.Main import ProfilerRL
    from LumensalisCP.HTTP.BSR import BSR_profileRL
    from LumensalisCP.HTTP import ControlVarsRL
    modules = [ ManagerRL, ProfilerRL,  BSR_profileRL, ControlVarsRL, BasicServerRL ]
    for m in modules:
        reload( m )
    self.cvHelper = None
    return modules

from LumensalisCP.Main.PreMainConfig import *

def BSR_cmd(self:BasicServer, request:Request, cmd:Optional[str]=None, **kwds:StrAnyDict ) -> JSONResponse | Response:
    """
    """
    
    try:
        # Get objects
        print( f"BSR_cmd cmd={repr(cmd)} received...")
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
            
        return JSONResponse(request, {"unknown command":cmd} )
    
    except Exception as inst:
        return ExceptionResponse(request, inst, "cmd failed" )
    
    return JSONResponse(request, {"message": "oops, command not handled..."})

__sayBSR_cmdRLImport.complete()