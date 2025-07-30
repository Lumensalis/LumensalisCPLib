from .common import *

from LumensalisCP.Main.PreMainConfig import pmc_getReloadableImportProfiler
__sayHTTPBSRProfileRLImport = pmc_getReloadableImportProfiler( "HTTP.BSR.BSRprofileRL" )

import LumensalisCP.Main.ProfilerRL


def BSR_profile(self:BasicServer.BasicServer, request:Request):
    
    try:
        # Get objects
        if request.method == GET:
            print(f"BSR_profile: request = {request}")
            print(f"BSR_profile: printDumpInterval = {pmc_gcManager.printDumpInterval}")
            info = LumensalisCP.Main.ProfilerRL.getProfilerInfo(self.main)
            return JSONResponse(request, info)
 
    except Exception as inst:
        return ExceptionResponse(request, inst, "profile failed" )
    return JSONResponse(request, {"message": "Something went wrong"})


__sayHTTPBSRProfileRLImport.complete(globals())
