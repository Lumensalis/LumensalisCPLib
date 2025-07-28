from .common import *

from LumensalisCP.Main.PreMainConfig import ReloadableImportProfiler
__sayHTTPBSRProfileRLImport = ReloadableImportProfiler( "HTTP.BSR.BSRprofileRL" )

from LumensalisCP.Main.Profiler import ProfileFrameBase, ProfileWriteConfig
import LumensalisCP.simple.profilingRL as profilingRL 

def BSR_profile(self:BasicServer.BasicServer, request:Request):
    
    try:
        # Get objects
        if request.method == GET:
            info = profilingRL.getProfilerInfo(self.main)
            return JSONResponse(request, info)
            lines:list[str] = []
            dumpConfig = ProfileWriteConfig(target=lines,
                minE = 0.000,
                minF=0.015,
                minSubF = 0.005,
                minB = 0,
            )
                    
            main = self.main
            context = main.getContext()
            i = context.updateIndex
            
            with dumpConfig.nestList('frames'):
                count = 10
                while count and i >= 0:
                    count -= 1
                    frame = main.profiler.timingForUpdate( i )
                    
                    if frame is not None:
                        frame.writeOn( dumpConfig )
                    i -= 1

            return JSONResponse(request, { "lines": lines })

        # Upload or update objects
        if request.method in {POST, PUT}:
            requestJson = request.json() # type:ignore[reportAttributeAccessIssue]
            if requestJson is not None and 'autoreload' in requestJson:
                autoreload:bool = requestJson['autoreload'] # type:ignore[reportAttributeAccessIssue]
                self.infoOut( "setting autoreload to %r", autoreload )
                supervisor.runtime.autoreload = autoreload


        return JSONResponse(request, getStatusInfo(self, request) )
    except Exception as inst:
        return ExceptionResponse(request, inst, "profile failed" )
    return JSONResponse(request, {"message": "Something went wrong"})


__sayHTTPBSRProfileRLImport.complete()
