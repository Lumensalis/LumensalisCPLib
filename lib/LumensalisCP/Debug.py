from __future__ import annotations
# pylint: disable=unused-import,import-error
#   pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayDebugImport = getImportProfiler( globals() ) # "Debug"

from LumensalisCP.Temporal.Time import getOffsetNow, TimeInSeconds 

try:
    #import typing
    from typing import NoReturn, Never, Optional, ClassVar, Any, TypeAlias, Protocol, TYPE_CHECKING
    KWDS_TYPE: TypeAlias = dict[str, Any]  # keyword arguments dictionary
except ImportError:
    TYPE_CHECKING = False # type: ignore
    
import traceback, time

from LumensalisCP.util.CountedInstance import CountedInstance


if TYPE_CHECKING:
    class IDebuggable(Protocol):
        
        @property
        def dbgName(self) -> str: ...
        @property
        def enableDbgOut(self) -> bool: ...

        def dbgOut( self, fmtString:str, *args:Any, **kwds:KWDS_TYPE ) -> None: ...
        def startupOut( self, fmtString:str, *args:Any, **kwds:KWDS_TYPE ) -> None: ...
        def infoOut( self, fmtString:str, *args:Any, **kwds:KWDS_TYPE ) -> None: ...
        def errOut( self, fmtString:str, *args:Any, **kwds:KWDS_TYPE ) -> None: ...
        def warnOut( self, fmtString:str, *args:Any, **kwds:KWDS_TYPE ) -> None: ...
        def SHOW_EXCEPTION( self,  inst:Exception, fmtString:str, *args:Any, **kwds:Any) -> None: ...

else:
    class IDebuggable: ...


class Debuggable( CountedInstance, IDebuggable ):
    DBG_HEADER_FORMAT: ClassVar[str] = "%.3f %s %s : "

    @staticmethod
    def _getNewNow():
        return getOffsetNow()
    
    def __init__(self, enableDbgOut:bool = False):
        CountedInstance.__init__(self)
        #IDebuggable.__init__(self)
        self.__dbgOutEnabled = enableDbgOut
        #self._DebuggableCachedName = None # type: Optional[str] # pylint: disable=attribute-defined-outside-init
        self.__dbgOutEnabled = enableDbgOut
    
    @staticmethod
    def __formatArgs( fmtString:str, args:list ) -> str: # pylint: disable=unused-private-member # type: ignore
        try: return fmtString % args 
        except Exception as inst: # pylint: disable=broad-exception-caught
            return f"could not format {fmtString:r}, {inst}"
        
    @property
    def dbgName(self) -> str:
        name = getattr(self,'name',None) or getattr( self, '_DebuggableCachedName', None )
        if name is not None: return name
        self._DebuggableCachedName = f"{self.__class__.__name__}@{id(self):X}" # pylint: disable=attribute-defined-outside-init
        return self._DebuggableCachedName
    
    
    def __header( self, kind:str )->str:
        return Debuggable.DBG_HEADER_FORMAT % (Debuggable._getNewNow(), kind, self.dbgName )
        #return "%.3f %s %s : " % (LumensalisCP.Main.Manager.MainManager.theManager.newNow, kind, self.dbgName )
    
    def __format( self, kind:str, fmtString:str, args:tuple[Any], kwds:KWDS_TYPE ) -> str: # pylint: disable=unused-argument
        try:
            msg = self.__header(kind) + (  fmtString % args )
            return msg
        except Exception as inst: # pylint: disable=broad-exception-caught
            return f"error formatting {kind} {fmtString} : {inst}"
    
    def dbgOut( self, fmtString:str, *args:Any, **kwds:KWDS_TYPE ):
        if self.__dbgOutEnabled:
            print( self.__format("", fmtString, args, kwds ) )

    
    def startupOut( self, fmtString:str, *args:Any, **kwds:KWDS_TYPE ):
        print( self.__format("STARTUP", fmtString, args, kwds ) )
            
    def infoOut( self, fmtString:str, *args:Any, **kwds:KWDS_TYPE ):
        print( self.__format("INFO", fmtString, args, kwds ) )
        
    def errOut( self, fmtString:str, *args:Any, **kwds:KWDS_TYPE ):
        print( self.__format("ERROR", fmtString, args, kwds ) )

    def warnOut( self, fmtString:str, *args:Any, **kwds:KWDS_TYPE ):
        print( self.__format("WARNING", fmtString, args, kwds ) )

    def SHOW_EXCEPTION( self,  inst:Exception, fmtString:str, *args:Any, **kwds:Any) -> None:
        print( self.__format("EXCEPTION", fmtString, args, kwds ) )
        print( f"{inst}\n{''.join(traceback.format_exception(inst))}" )

    def setEnableDebugWithChildren( self, setting:bool, *args:Any, **kwds:Any ) -> None:
        self.enableDbgOut = setting
        self._derivedSetEnableDebugWithChildren( setting, *args, **kwds)
        
    def _derivedSetEnableDebugWithChildren( self, setting:bool, *args:Any, **kwds:Any ) -> None:
        pass
            
    @property
    def enableDbgOut(self) -> bool: return self.__dbgOutEnabled
    
    @enableDbgOut.setter
    def enableDbgOut(self,enabled:bool): self.__dbgOutEnabled = enabled

_sayDebugImport.complete(globals())
