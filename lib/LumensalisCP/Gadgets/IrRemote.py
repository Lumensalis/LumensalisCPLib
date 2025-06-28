
import pulseio, adafruit_irremote


from LumensalisCP.IOContext  import * # NamedOutputTarget, EvaluationContext, UpdateContext, InputSource
from LumensalisCP.Main.Manager import MainManager

from LumensalisCP.Triggers.Timer import PeriodicTimer
from  LumensalisCP.Main.Dependents import MainChild
import json

class LCP_IRrecv(MainChild):
    REMOTES_CATALOG_FILENAME = '/remotes.json'
    RemoteCatalog = {
        "ar_mp3" : {
            "CH-": 0xffa25d,
            "CH": 0xff629d,
            "CH+": 0xffe21d,
            "PREV": 0xff22dd,
            "NEXT": 0xFF02FD,
            "PLAY": 0xffc23d,
            "VOL-": 0xffe01f,
            "VOL+": 0xffa857,
        }
    }
    
    def __init__(self, pin, codenames:Mapping = {}, main:MainManager = None, name:str|None = None, updateInterval = 0.1 ):
        super().__init__(name=name or LCP_IRrecv.__name__, main=main )
        self.pulseIn = pulseio.PulseIn(pin, maxlen=120, idle_state=True)
        self.decoder = adafruit_irremote.GenericDecode()
        self.__callbacksByCode:Mapping[int,Callable] = {}
        self.__unhandledCallback = None
        self.__updateInterval = updateInterval
        self.__jsonCatalog = None
        
        if type(codenames) is str:
            builtinCodes = LCP_IRrecv.RemoteCatalog.get(codenames,None)
            if builtinCodes is not None:
                codenames = builtinCodes
            else:
                codes = self.jsonCatalog.get( codenames,None )
                ensure( codes is not None, "could not find %r in remotes catalog", codenames )
                codenames = codes
            
        self.codenames:Mapping(str,int) = codenames

        self._checkTimer = PeriodicTimer( updateInterval , manager=main.timers, name=f"{self.name}Check" )
        
        def checkPulse(**kwds):
            # print( "HKA check pulse...")
            self.check(**kwds)
            
        self._checkTimer.addAction( checkPulse )
        
        def startIrTimer():
            #print( f"starting keep alive timer with {self.__keepAlivePulse}")
            self._checkTimer.start(self.__updateInterval)
            
        main.callLater( startIrTimer )

    @property
    def jsonCatalog(self) -> Mapping[str,int]:
        if self.__jsonCatalog is None:
            remotes = {}
            try:
                with open( self.REMOTES_CATALOG_FILENAME, 'r') as f:
                    remotes = json.load(f)
            except Exception as inst:
                print( f"failed to load {self.REMOTES_CATALOG_FILENAME} : {inst}")
            self.__jsonCatalog = remotes
        return self.__jsonCatalog
    
    def handleRawCode(self, rawCode ):
        code = 0
        for byte in rawCode:
            code = (code *256) + byte
            
            
        cb = self.__callbacksByCode.get(code,None) # self.__unhandledCallback)
        if cb is not None:
            if 1: self.dbgOut( f"calling callback for code {'x'%code}, cb={cb}" )
            cb()
        else:
            self._unhandled(code, rawCode)
        
    def _unhandled(self, code, rawCode ):
        
        if self.__unhandledCallback is not None:
            try:
                self.__unhandledCallback( code=code, rawCode=rawCode)
            except Exception as inst:
                self.SHOW_EXCEPTION( inst, "unhandledCallback failed for %x from %r", code, rawCode )
        else:
            self.dbgOut( f"unhandled remote code: 0x{'%x'%code} from {rawCode}" )

    def setUnhandledCallback( self, cb:Callable ):
        self.__unhandledCallback = cb

    def onUnhandledDef( self ):
        def on2( callable ):
            self.setUnhandledCallback( callable )
            return callable
        
        return on2

    def addCallbackForCode(self, code:int|str, cb:Callable ):
        if type(code) is str:
            code = self.codenames[code]

        dictAddUnique(self.__callbacksByCode, code, cb )

    def onCodeDef( self, code:int|str ):
        
        def on2( callable ):
            self.addCallbackForCode( code, callable )
            return callable
        return on2

    def onCode( self, code:int|str=None, action:Callable = None ):
        assert code is not None
        assert action is not None
        self.addCallbackForCode( code, action )
        
    def check( self, **kwds ):
        pulses = self.decoder.read_pulses(self.pulseIn, blocking=False)
        if pulses is None or len(pulses) == 0: return
        # print("Heard", len(pulses), "Pulses:", pulses)
        try:
            code = self.decoder.decode_bits(pulses)
            
            self.handleRawCode( code )
        except adafruit_irremote.IRNECRepeatException:  # unusual short code!
            self.dbgOut("NEC repeat!")
        except (
            adafruit_irremote.IRDecodeException,
            adafruit_irremote.FailedToDecode,
        ) as e:  # failed to decode
            self.dbgOut("Failed to decode: %s", e.args)

    
def onIRCode( ir: LCP_IRrecv, code:int|str ):
        
    def on2( callable ):
        ir.addCallbackForCode( code, callable )
        return callable
    return on2