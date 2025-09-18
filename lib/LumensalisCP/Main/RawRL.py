from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( __name__, globals(), reloadable=True )

# pylint: disable=redefined-builtin,unused-variable,unused-argument,broad-exception-caught
# pyright: reportUnusedImport=false
import digitalio
import pulseio

from LumensalisCP.IOContext import *


from LumensalisCP.pyCp.importlib import reload
from LumensalisCP.util.Reloadable import ReloadableModule

if TYPE_CHECKING:
    from LumensalisCP.Behaviors.Rotation import DCMotorSpinner
    from LumensalisCP.Main.Raw import RawAccess, RawPWMInputWrapper

_sayImport.parsing()

#############################################################################
# pyright: reportPrivateUsage=false

_rawModule = ReloadableModule( 'LumensalisCP.Main.Raw' )
_RawPWMInputWrapper = _rawModule.reloadableClassMeta('RawPWMInputWrapper', stripPrefix='RawPWMInputWrapper_')

rlData = {
    'cycles': 0,
    'pulsesDetected': 0,
    'onCount': 0,
    'offCount': 0,
    'onTotal': 0,
    'offTotal': 0,
    'lastState': None,
    'boopIndex': 0,
}

def bar( context:Optional[EvaluationContext]=None ) -> None:
    print( "bar()..." )
    
#@_RawPWMInputWrapper.reloadableMethod()
def RawPWMInputWrapper_rl( self:RawPWMInputWrapper, context:Optional[EvaluationContext]=None )  -> None:  
    
    self.infoOut( "rl : importing LumensalisCP.Main.RawRL" )
    from LumensalisCP.Main import RawRL
    self.infoOut( "rl : reloading LumensalisCP.Main.RawRL" )
    reload(RawRL)
    pass

#@_RawPWMInputWrapper.reloadableMethod()
def RawPWMInputWrapper_boop( self:RawPWMInputWrapper, context:Optional[EvaluationContext]=None )  -> None:  
    global rlData
    context = UpdateContext.fetchCurrentContext(context)
    priorIndex = rlData.get('boopIndex', 0)
    index= context.updateIndex
    rlData['boopIndex'] = index
    if index == priorIndex:
        self.infoOut( "boop : ignoring duplicate index %r", index )
    else:
        self.pulseIn.deinit()
        self.pulseIn = pulseio.PulseIn(self.pin, maxlen=128, idle_state=False)
        
        rlData['verbose'] = not rlData.get('verbose', False)
    self.infoOut( "boop @ %r: verbose=%r index=%r priorIndex=%r" % (id(RawPWMInputWrapper_boop), rlData['verbose'], index, priorIndex) )

print( f"reloaded {RawPWMInputWrapper_boop} @{id(RawPWMInputWrapper_boop)}" )
#@_RawPWMInputWrapper.reloadableMethod()
def RawPWMInputWrapper_getDerivedValue(self:RawPWMInputWrapper, context:EvaluationContext) -> Any:

    if False:
        rv = getattr(self, 'temp_rv', 0 )
        rv += 1
        if rv > 100: rv = 0
        self.temp_rv = rv


        #self.infoOut("getDerivedValue() -> %r", rv )
        return rv
    
    global rlData
    verbose = rlData.get('verbose', False)

    if rlData['cycles'] == 0:
        # first call after import OR reload
        self.infoOut("%s getDerivedValue() after RL...", self.__class__.__name__ )

        rlData['cycles'] = 1

        #self.pulseIn.deinit()
        #self.pulseIn = pulseio.PulseIn(self.pin, maxlen=128) #, idle_state=False)
        pass

    if verbose:
        self.infoOut("getDerivedValue() called, len(pulseIn)=%r paused=%r maxlen=%r state=%r",
                     len(self.pulseIn), self.pulseIn.paused, self.pulseIn.maxlen, 
                     bool(self.pulseIn) )

    try:
        rlData['cycles'] = rlData.get('cycles',0) + 1

        if self.pulseIn.paused:
            self.infoOut( "clearing paused pulseIn" )
            self.pulseIn.clear()
            self.pulseIn.resume()
            return -1
        
        count = len(self.pulseIn)
        if count == 0:
            return -1

        self.pulsesDetected.set( self.pulsesDetected.latestSimpleValue+count, context )
        
        self.readCycles.set( self.readCycles.latestSimpleValue+1, context )

        self.pulseIn.pause()
        p1 = self.pulseIn[count-2]
        p2 = self.pulseIn[count-1]
        assert isinstance( p1, int )
        assert isinstance( p2, int )
        if p1 > p2:
            if count > 2:
                p2 = p1
                p1 = self.pulseIn[count-3]
            else:
                pTemp = p1
                p1 = p2
                p2 = pTemp
        
        self.pulseIn.resume()

    



        assert p2 > 0
        rv = (p1 + p2 ) / p1
        self.pulseIn.clear()
        self.infoOut("getDerivedValue() -> %r (p1=%r,p2=%r) count=%r cycles=%r ", rv, 
                    p1, p2,  count, rlData['cycles'] )
        return rv


        #return self._io.value
    except Exception as inst: # pylint: disable=broad-exception-caught
        self.SHOW_EXCEPTION( inst, "getDerivedValue() failed" )

#############################################################################

_sayImport.complete(globals())