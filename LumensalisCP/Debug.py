
import LumensalisCP
import LumensalisCP.Main
import LumensalisCP.Main.Manager
import traceback
#mm =  LumensalisCP.Main.Manager 

class Debuggable( object ):
    
    
    def __init__(self):
        self.__dbgOutEnabled = False
        
    @property
    def dbgName(self):
        return getattr(self,'name',None) or self.__class__.__name__ 
    
    def __header( self, kind:str )->str:
        return "%.3f %s %s : " % (LumensalisCP.Main.Manager.MainManager.theManager.newNow, kind, self.dbgName )
    
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
    def dbgOutEnabled(self) -> bool: return self.__dbgOutEnabled
    
    @dbgOutEnabled.setter
    def dbgOutEnabled(self,enabled:bool): self.__dbgOutEnabled = enabled