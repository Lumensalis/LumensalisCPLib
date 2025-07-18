


from LumensalisCP.IOContext  import * # NamedOutputTarget, EvaluationContext, UpdateContext, InputSource
from LumensalisCP.commonCP import *
from LumensalisCP.Main.Manager import MainManager

from LumensalisCP.Triggers.Timer import PeriodicTimer
from  LumensalisCP.Main.Dependents import MainChild

import adafruit_irremote   # pyright: ignore[reportMissingImports]
import json
import pulseio

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
        },
        "dvd_remote": {
            "DOWN":0x59a66a95,
            "UP" : 0x59a6f20d,
            "PREV": 0x59a6609f,
            "NEXT": 0x59a640bf,
            "PLAY": 0x59a6c03f,
            "STOP": 0x59a6f00f,
            "PAUSE": 0x59a6d827,
            "MENU": 0x59a6fa05,
            "0": 0x59a60af5,
            "1": 0x59a65aa5,
            "2": 0x59a67a85,
            "3": 0x59a6728d,
            "4": 0x59a6ba45,
            "5": 0x59a68a75,
            "6": 0x59a6926d,
            "7": 0x59a69a65,
            "8": 0x59a6aa55,
            "9": 0x59a6b24d,
            
        }
        
         # 0xacd3354a
    }
    
    showUnhandled:bool
    
    def __init__(self, pin, main:MainManager,  codenames:Mapping[str,int]|str|None = {},
                 name:str|None = None, updateInterval = 0.1,
                 showUnhandled = False ):
        super().__init__( main=main, name=name )
        maxLen = 128
        self.showUnhandled = showUnhandled 
        try:
            self.pulseIn = pulseio.PulseIn(pin, maxlen=maxLen, idle_state=True)
        except Exception as inst:
            SHOW_EXCEPTION( inst, f"failed initializing pulseio.PulseIn({pin}, maxlen={maxLen}, idle_state=True)")
            raise
        
        self.decoder = adafruit_irremote.GenericDecode()
        self.__callbacksByCode:dict[int,Callable] = {}
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
            
        self.codenames:Mapping[str,int] = codenames

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
        self.enableDbgOut and self.dbgOut( f"handleRawCode {rawCode}" )
        for byte in rawCode:
            code = (code *256) + byte
            
        
        
        cb = self.__callbacksByCode.get(code,None) # self.__unhandledCallback)
        if cb is not None:
            self.enableDbgOut and self.dbgOut( f"calling callback for code {code}, cb={cb}" )
            cb()
        else:
            self._unhandled(code, rawCode)
        
    def _unhandled(self, code, rawCode ):
        
        if self.__unhandledCallback is not None:
            try:
                self.__unhandledCallback( code=code, rawCode=rawCode)
            except Exception as inst:
                self.SHOW_EXCEPTION( inst, "unhandledCallback failed for %x from %r", code, rawCode )
        #else:
        #    self.enableDbgOut and self.dbgOut( f"unhandled remote code: 0x{'%x'%code} from {rawCode}" )
        if self.showUnhandled: 
            self.infoOut( f"unhandled remote code: 0x{'%x'%code} from {rawCode}" )

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

    def onCode( self, code:int|str, action:Callable  ):
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
            self.enableDbgOut and self.dbgOut("NEC repeat!")
        except (
            adafruit_irremote.IRDecodeException,
            adafruit_irremote.FailedToDecode,
        ) as e:  # failed to decode
            self.enableDbgOut and self.dbgOut("Failed to decode: %r /  %s %r", pulses, e.args, e )

    
def onIRCode( ir: LCP_IRrecv, code:int|str ):
        
    def on2( callable ):
        ir.addCallbackForCode( code, callable )
        return callable
    return on2