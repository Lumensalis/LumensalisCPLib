
import pulseio, adafruit_irremote

from LumensalisCP.Main.Expressions import InputSource, OutputTarget, EvaluationContext, UpdateContext
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.common import *

from LumensalisCP.Triggers.Timer import PeriodicTimer
from LumensalisCP.CPTyping import *
from  LumensalisCP.Main.Dependents import MainChild


class LCP_IRrecv(MainChild):
    
    def __init__(self, pin, codenames:Mapping = {}, main:MainManager = None, name:str|None = None, updateInterval = 0.1 ):
        super().__init__(name=name or LCP_IRrecv.__name__, main=main )
        self.pulseIn = pulseio.PulseIn(pin, maxlen=120, idle_state=True)
        self.decoder = adafruit_irremote.GenericDecode()
        self.__callbacksByCode:Mapping[int,Callable] = {}
        self.__unhandledCallback = self._unhandled
        self.__updateInterval = updateInterval
        self.codenames = codenames

        self._checkTimer = PeriodicTimer( updateInterval , manager=main.timers, name=f"{self.name}Check" )
        
        def checkPulse(**kwds):
            # print( "HKA check pulse...")
            self.check(**kwds)
            
        self._checkTimer.addAction( checkPulse )
        
        def startIrTimer():
            #print( f"starting keep alive timer with {self.__keepAlivePulse}")
            self._checkTimer.start(self.__updateInterval)
            
        main.callLater( startIrTimer )


    def handleRawCode(self, rawCode ):
        code = 0
        for byte in rawCode:
            code = (code *256) + byte
            
            
        cb = self.__callbacksByCode.get(code,None) # self.__unhandledCallback)
        if cb is not None:
            if 1: self.dbgOut( f"calling callback for code {"%x"%code}, cb={cb}")
            cb()
        else:
            self._unhandled(code, rawCode)
        
    def _unhandled(self, code, rawCode ):
        self.errOut( f"unhandled remote code: 0x{"%x"%code} from {rawCode}" )
        

    def setUnhandledCallback( self, cb:Callable ):
        self.__unhandledCallback = cb
        
    def addCallbackForCode(self, code:int|str, cb:Callable ):
        if type(code) is str:
            code = self.codenames[code]

        dictAddUnique(self.__callbacksByCode, code, cb )

    def onCode( self, code:int|str=None, action:Callable = None ):
        assert code is not None
        assert action is not None
        self.addCallbackForCode( code, action )
        
    def check( self, **kwds ):
        pulses = self.decoder.read_pulses(self.pulseIn, blocking=False)
        if pulses is None: return
        # print("Heard", len(pulses), "Pulses:", pulses)
        try:
            code = self.decoder.decode_bits(pulses)
            
            self.handleRawCode( code )
        except adafruit_irremote.IRNECRepeatException:  # unusual short code!
            self.warnOut("NEC repeat!")
        except (
            adafruit_irremote.IRDecodeException,
            adafruit_irremote.FailedToDecode,
        ) as e:  # failed to decode
            self.warnOut("Failed to decode: %s", e.args)

    
def onIRCode( ir: LCP_IRrecv, code:int|str ):
        
    def on2( callable ):
        ir.addCallbackForCode( code, callable )
        return callable
    return on2