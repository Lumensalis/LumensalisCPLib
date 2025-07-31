from .common import *

from LumensalisCP.ImportProfiler import getImportProfiler
__sayHTTPBSRProfileRLImport = getImportProfiler( globals(), reloadable=True  )

import LumensalisCP.Main.ProfilerRL
from LumensalisCP.Main.Profiler import ProfileWriteConfig   
from collections import OrderedDict

def BSR_profile(self:BasicServer.BasicServer, request:Request):
    
    try:
        # Get objects
        if request.method == GET:
            print(f"BSR_profile: request = {request}")
            print(f"BSR_profile: printDumpInterval = {pmc_gcManager.printDumpInterval}")

            info:StrAnyDict = OrderedDict()
            settings = dict(
                    minE = 0.005,
                    minF=0.01,
                    minSubF = 0.05,
                    minB = 0,
                    minEB = 0,
            )

            dumpConfig = ProfileWriteConfig(target=info, **settings )

            print( f"getProfilerInfo: settings = {settings}" )
            self.main.profiler.getProfilerInfo(dumpConfig=dumpConfig)
            return JSONResponse(request, info)
 
    except Exception as inst:
        return ExceptionResponse(request, inst, "profile failed" )
    return JSONResponse(request, {"message": "Something went wrong"})


__sayHTTPBSRProfileRLImport.complete()
