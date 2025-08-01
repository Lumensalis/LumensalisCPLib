from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayImport = getImportProfiler( __name__, globals() )

import json

import pulseio
import adafruit_irremote    # pylint: disable=import-error # type: ignore

from LumensalisCP.IOContext  import * # NamedOutputTarget, EvaluationContext, UpdateContext, InputSource
from LumensalisCP.commonCP import *

from LumensalisCP.Main.Dependents import MainChild

if TYPE_CHECKING:

    IRUnhandledCallbackType:TypeAlias = Callable[[int, list[int]], None]
    IRCallbackType:TypeAlias = Callable[[], None]

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
    
    class KWDS( MainChild.KWDS ):
        #refreshRate: NotRequired[TimeInSecondsConfigArg]
        showUnhandled: NotRequired[bool]
        codenames: NotRequired[dict[str,int]|str|None]
        
    showUnhandled:bool
    codenames:dict[str,int]
    
    def __init__(self, pin:microcontroller.Pin,
                 codenames:dict[str,int]|str|None = {},
                 showUnhandled:bool = False ,
                **kwds:Unpack[MainChild.KWDS]
            ) -> None:
        super().__init__( **kwds )
        maxLen = 128
        self.showUnhandled = showUnhandled 
        try:
            self.pulseIn = pulseio.PulseIn(pin, maxlen=maxLen, idle_state=True)
        except Exception as inst:
            SHOW_EXCEPTION( inst, f"failed initializing pulseio.PulseIn({pin}, maxlen={maxLen}, idle_state=True)")
            raise
        
        self.decoder = adafruit_irremote.GenericDecode() # type: ignore
        self.__callbacksByCode:dict[int,IRCallbackType] = {}
        self.__unhandledCallback:IRUnhandledCallbackType|None = None
        #self.__updateInterval = refreshRate
        self.__jsonCatalog = None

        if isinstance(codenames, str):
            builtinCodes = LCP_IRrecv.RemoteCatalog.get(codenames, None)
            if builtinCodes is not None:
                codenames = builtinCodes
            else:
                codes = self.jsonCatalog.get( codenames,None )
                assert codes is not None, f"could not find {codenames} in remotes catalog"
                codenames = codes
            self.codenames = codenames
        elif codenames is None:
            self.codenames = {}
        else:
            assert not isinstance(codenames, str)
            self.codenames = codenames # type: ignore


    __jsonCatalog: dict[str,dict[str,int]]|None

    @property
    def jsonCatalog(self) ->  dict[str,dict[str,int]]:
        if self.__jsonCatalog is None:
            remotes:dict[str,dict[str,int]] = {}
            try:
                with open( self.REMOTES_CATALOG_FILENAME, 'r', encoding='utf-8') as f:
                    remotes = json.load(f)
                    assert remotes is not None
            except Exception as inst: # pylint: disable=broad-except
                print( f"failed to load {self.REMOTES_CATALOG_FILENAME} : {inst}")
                remotes = {}
                
            self.__jsonCatalog = remotes
        return self.__jsonCatalog
    
    def handleRawCode(self, rawCode:list[int] ):
        code = 0
        if self.enableDbgOut: self.dbgOut( f"handleRawCode {rawCode}" )
        for byte in rawCode:
            code = (code *256) + byte
            
        cb = self.__callbacksByCode.get(code,None) # self.__unhandledCallback)
        if cb is not None:
            if self.enableDbgOut: self.dbgOut( f"calling callback for code {code}, cb={cb}" )
            cb()
        else:
            self._unhandled(code, rawCode)
        
    def _unhandled(self, code:int, rawCode:list[int] ):
        
        if self.__unhandledCallback is not None:
            try:
                self.__unhandledCallback( code=code, rawCode=rawCode) # type: ignore
            except Exception as inst: # pylint: disable=broad-exception-caught
                self.SHOW_EXCEPTION( inst, "unhandledCallback failed for %x from %r", code, rawCode )
        #else:
        #    if self.enableDbgOut: self.dbgOut( f"unhandled remote code: 0x{'%x'%code} from {rawCode}" )
        if self.showUnhandled: 
            self.infoOut( f"unhandled remote code: 0x{'%x'%code} from {rawCode}" )

    def setUnhandledCallback( self, cb:IRUnhandledCallbackType ) -> None:
        self.__unhandledCallback = cb

    def onUnhandledDef( self ):
        def on2( callback:IRUnhandledCallbackType ) -> IRUnhandledCallbackType:
            self.setUnhandledCallback( callback )
            return callback
        
        return on2

    def addCallbackForCode(self, code:int|str, cb:IRCallbackType ):
        if isinstance(code, str):
            code = self.codenames[code]

        dictAddUnique(self.__callbacksByCode, code, cb )

    def onCodeDef( self, code:int|str ):
        
        def on2( callback:IRCallbackType ) -> IRCallbackType:
            self.addCallbackForCode( code, callback )
            return callback
        return on2

    def onCode( self, code:int|str, action:IRCallbackType  ) -> None:
        assert code is not None
        assert action is not None
        self.addCallbackForCode( code, action )
        
    #def check( self, context:EvaluationContext ) -> None:
    def derivedRefresh(self,context:'EvaluationContext') -> None:        
        # type: ignore
        if self.enableDbgOut: self.dbgOut( f"Checking IR remote {self.name} for codes")
        with context.subFrame('check', self.name ) as activeFrame:
            activeFrame.snap("read_pulses")
            pulses:list[int]|None = self.decoder.read_pulses(self.pulseIn, blocking=False)  # type: ignore
            if pulses is None or len(pulses) == 0: return # type: ignore
            # print("Heard", len(pulses), "Pulses:", pulses)
            try:
                activeFrame.snap("decode")
                code = self.decoder.decode_bits(pulses) # type: ignore
                activeFrame.snap("handleRawCode")
                self.handleRawCode( code )# type: ignore
            except adafruit_irremote.IRNECRepeatException:  # unusual short code! # type: ignore
                if self.enableDbgOut: self.dbgOut("NEC repeat!")
            except (
                adafruit_irremote.IRDecodeException, # type: ignore
                adafruit_irremote.FailedToDecode, # type: ignore
            ) as e:  # failed to decode # type: ignore
                if self.enableDbgOut: self.dbgOut("Failed to decode: %r /  %s %r", pulses, e.args, e ) # type: ignore

def onIRCode( ir: LCP_IRrecv, code:int|str ):
        
    def on2( callback:IRCallbackType ):
        ir.addCallbackForCode( code, callback )
        return callback
        
    return on2

_sayImport.complete()
