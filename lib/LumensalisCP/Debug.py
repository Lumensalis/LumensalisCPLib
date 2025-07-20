from __future__ import annotations

try:
    import typing
    from typing import NoReturn, Never, Optional
    
except ImportError:
    pass
    
import traceback, time

class Debuggable( object ):
    
    @staticmethod
    def _getNewNow():
        return time.monotonic()
    
    def __init__(self, enableDbgOut:bool = False):
        self.__dbgOutEnabled = enableDbgOut
    
    @staticmethod
    def __formatArgs( fmtString, args ) -> str: # pylint: disable=unused-private-member
        try: return fmtString % args 
        except Exception as inst: # pylint: disable=broad-exception-caught
            return f"could not format {fmtString:r}, {inst}"
        
    @property
    def _dbgName(self):
        name = getattr(self,'name',None) or getattr( self, '_DebuggableCachedName', None )
        if name is not None: return name
        self._DebuggableCachedName = f"{self.__class__.__name__}@{id(self):X}" # pylint: disable=attribute-defined-outside-init
        return self._DebuggableCachedName
    
    def __header( self, kind:str )->str:
        return "%.3f %s %s : " % (Debuggable._getNewNow(), kind, self._dbgName )
        #return "%.3f %s %s : " % (LumensalisCP.Main.Manager.MainManager.theManager.newNow, kind, self._dbgName )
    
    def __format( self, kind, fmtString:str, args, kwds ): # pylint: disable=unused-argument
        try:
            msg = self.__header(kind) + (  fmtString % args )
            return msg
        except Exception as inst: # pylint: disable=broad-exception-caught
            return f"error formatting {kind} {fmtString} : {inst}"
    
    def dbgOut( self, fmtString:str, *args, **kwds ):
        if self.__dbgOutEnabled:
            print( self.__format("", fmtString, args, kwds ) )

    
    def startupOut( self, fmtString:str, *args, **kwds ):
        print( self.__format("STARTUP", fmtString, args, kwds ) )
            
    def infoOut( self, fmtString:str, *args, **kwds ):
        print( self.__format("INFO", fmtString, args, kwds ) )
        
    def errOut( self, fmtString:str, *args, **kwds ):
        print( self.__format("ERROR", fmtString, args, kwds ) )

    def warnOut( self, fmtString:str, *args, **kwds ):
        print( self.__format("WARNING", fmtString, args, kwds ) )

    def SHOW_EXCEPTION( self,  inst:Exception, fmtString:str, *args, **kwds):
        print( self.__format("EXCEPTION", fmtString, args, kwds ) )
        print( f"{inst}\n{''.join(traceback.format_exception(inst))}" )

    def setEnableDebugWithChildren( self, setting:bool, *args, **kwds ):
        self.enableDbgOut = setting
        self._derivedSetEnableDebugWithChildren( setting, *args, **kwds )
        
    def _derivedSetEnableDebugWithChildren( self, setting:bool, *args, **kwds ):
        pass
            
    @property
    def enableDbgOut(self) -> bool: return self.__dbgOutEnabled
    
    @enableDbgOut.setter
    def enableDbgOut(self,enabled:bool): self.__dbgOutEnabled = enabled
