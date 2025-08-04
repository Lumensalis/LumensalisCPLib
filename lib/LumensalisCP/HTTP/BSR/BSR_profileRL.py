

from adafruit_httpserver.response import JSONResponse, Response
from LumensalisCP.ImportProfiler import getImportProfiler
__sayHTTPBSRProfileRLImport = getImportProfiler( globals(), reloadable=True  )

from LumensalisCP.HTTP.BSR.common import *
from LumensalisCP.Main.Profiler import ProfileWriteConfig   


from LumensalisCP.util.Reloadable import ReloadableModule

_module = ReloadableModule( 'LumensalisCP.HTTP.BasicServer' )
_BasicServer = _module.reloadableClassMeta('BasicServer')

@_BasicServer.reloadableMethod()
def BSR_profile(self:BasicServer, request:Request) -> JSONResponse | Response:
    
    try:
        # Get objects
        if request.method == GET:
            print(f"BSR_profile: request = {request}")
            print(f"BSR_profile: printDumpInterval = {pmc_gcManager.printDumpInterval}")

            info:StrAnyDict = OrderedDict()
            settings: ProfileWriteConfig.KWDS = {
                'target': info,
                'minE': 0.005,
                'minF': 0.01,
                'minSubF': 0.05,
                'minB': 0,
                'minEB': 0,
            }
            dumpConfig = ProfileWriteConfig( **settings )

            print( f"getProfilerInfo: settings = {settings}" )
            self.main.profiler.getProfilerInfo(dumpConfig=dumpConfig)
            return JSONResponse(request, info)
 
    except Exception as inst:
        return ExceptionResponse(request, inst, "profile failed" )
    return JSONResponse(request, {"message": "Something went wrong"})


__sayHTTPBSRProfileRLImport.complete()
