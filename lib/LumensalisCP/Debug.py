
import traceback, time

class Debuggable( object ):
    @staticmethod
    def _getNewNow():
        ns = time.monotonic_ns()
        return ns * 0.000000001
        #return LumensalisCP.Main.Manager.MainManager.theManager.newNow
    
    def __init__(self):
        self.__dbgOutEnabled = False
        
    @property
    def _dbgName(self):
        return getattr(self,'name',None) or self.__class__.__name__ 
    
    def __header( self, kind:str )->str:
        return "%.3f %s %s : " % (Debuggable._getNewNow(), kind, self._dbgName )
        #return "%.3f %s %s : " % (LumensalisCP.Main.Manager.MainManager.theManager.newNow, kind, self._dbgName )
    
    def __format( self, kind, fmtString:str, args, kwds ):
        try:
            msg = self.__header(kind) + (  fmtString % args )
            return msg
        except Exception as inst:
            return f"error formatting {kind} {fmtString} : {inst}"
        
    def dbgOut( self, fmtString:str, *args, **kwds ):
        if self.__dbgOutEnabled:
            print( self.__format("", fmtString, args, kwds ) )

    def infoOut( self, fmtString:str, *args, **kwds ):
        print( self.__format("INFO", fmtString, args, kwds ) )
        
    def errOut( self, fmtString:str, *args, **kwds ):
        print( self.__format("ERROR", fmtString, args, kwds ) )

    def warnOut( self, fmtString:str, *args, **kwds ):
        print( self.__format("WARNING", fmtString, args, kwds ) )
            
            
    def SHOW_EXCEPTION( self,  inst:Exception, fmtString:str, *args, **kwds):
        print( self.__format("EXCEPTION", fmtString, args, kwds ) )
        print( f"{inst}\n{''.join(traceback.format_exception(inst))}" )
        
    @property
    def enableDbgOut(self) -> bool: return self.__dbgOutEnabled
    
    @enableDbgOut.setter
    def enableDbgOut(self,enabled:bool): self.__dbgOutEnabled = enabled