from LumensalisCP.CPTyping import *
from LumensalisCP.Debug import Debuggable
from LumensalisCP.common import *

import LumensalisCP.Main
from LumensalisCP.Main.Profiler import ProfileFrame, ProfileSubFrame, ProfileStubFrame
import LumensalisCP.Main.Releasable

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    import LumensalisCP.Main.Manager 
    from  LumensalisCP.Main.Expressions import EvaluationContext
    from LumensalisCP.Inputs import InputSource
    DirectValue = Type("int|bool|float|RGB")
    OptionalContextArg = Optional[EvaluationContext]

    
class UpdateContextDebugManager(LumensalisCP.Main.Releasable.Releasable):
    def __init__( self ):
        #self.context:EvaluationContext|None = None
        self.debugEvaluate = True
        
    def prepare( self, context:EvaluationContext, debugEvaluate = True ):
        self.context = context
        self.debugEvaluate = debugEvaluate

    def __enter__(self):
        assert self.context is not None
        self.prior_debugEvaluate = self.context.debugEvaluate
        self.prior_debugIndent = self.context._debugIndent
        self.context.debugEvaluate = self.debugEvaluate
        self.context._debugIndent = self.debugIndent = self.prior_debugIndent + 2
        return self

    def __exit__(self, eT, eV, eTB ):
        assert self.context is not None
        self.context.debugEvaluate = self.prior_debugEvaluate
        self.context._debugIndent = self.prior_debugIndent 
        self.context = None

    def say( self, instanceOrMessage:Debuggable|str, *args ) -> None:
        if type(instanceOrMessage) is str:
            message = instanceOrMessage
            instance = None
        else:
            instance = instanceOrMessage
            assert isinstance( instance, Debuggable )
            assert len(args) > 0
            message = args[0]
            assert type(message) is str
            args = args[1:]
        pfx = "                       "[:self.debugIndent] + "nde| "
        if len(args): message = safeFmt(message,*args)
            
        self.context.infoOut( "NDE %.32s %s %s",
                             "" if instance is None else instance._dbgName,
                              "                       "[:self.debugIndent],
                             message )

    def releaseNested(self):
        self.context = None
        
class UpdateContext(Debuggable):
    activeFrame: ProfileFrame
    
    _stubFrame = ProfileStubFrame( )
    
    def __init__( self, main:MainManager=None ):
        super().__init__()
        #print( f"NEW UpdateContext @{id(self):X}")
        self.__updateIndex = 0
        self.__changedSources : list[InputSource] = []
        self.__mainRef = main.makeRef()
        self.__when = main.when
        self.activeFrame = None
        self.baseFrame = None
        self.debugEvaluate = False
        self._debugIndent = 0

    @classmethod
    def _patch_fetchCurrentContext(cls, main:MainManager):
        assert main is not None
        assert main._privateCurrentContext is not None
        def patchedFetchCurrentContext( context:EvaluationContext|None ) -> EvaluationContext:
            return context or main._privateCurrentContext
        cls.fetchCurrentContext = patchedFetchCurrentContext
        
    def nestDebugEvaluate(self, debugEvaluate:bool|None = True ) -> UpdateContextDebugManager:
        entry = UpdateContextDebugManager.releasableGetInstance()
        entry.prepare( self,debugEvaluate if debugEvaluate is not None else self.debugEvaluate)
        return entry
    
    def reset( self, when:TimeInMS|None = None ):
        try:
            self.__updateIndex += 1
            #self.__changedSources.clear()
            self.__when = when or self.main.when
            self.activeFrame = None
            self.baseFrame = None
            self._debugIndent = 0
        except Exception as inst:
            print( f"UpdateContext.refresh @{id(self):X} failed : {inst}")
            raise
        
    @property
    def main(self) -> MainManager: return self.__mainRef()
        
    @property
    def when(self) -> TimeInSeconds : return self.__when
    
    @property
    def updateIndex(self) -> int: return self.__updateIndex

    @property
    def changedSources(self): 
        raise NotImplemented
        return self.__changedSources
    
    def subFrame(self, name:str|None=None, name2:str|None=None) -> ProfileSubFrame:
        #rv = self.activeFrame.activeFrame().subFrame(self, name, name2)
        rv = self.activeFrame.subFrame(self, name, name2)
        return rv
    
    def stubFrame(self, name:str|None=None, name2:str|None=None) -> ProfileStubFrame:
        return UpdateContext._stubFrame
        
    def addChangedSource( self, changed:InputSource):
        #self.__changedSources.append( changed )
        pass
        
    def valueOf( self, value:Any ) -> Any:
        raise NotImplemented
    
        
    @staticmethod
    def fetchCurrentContext( context:EvaluationContext|None ) -> EvaluationContext:
        """return context if it is not None, otherwise return the current
        context from the MainManager singleton

        :param context: the (potentially None) context to try first
        :type context: UpdateContext | None
        :return: the current context
        :rtype: UpdateContext
        """
        raise NotImplemented
        

#############################################################################


#############################################################################
class RefreshCycle(object):
    def __init__(self, refreshRate:TimeInSeconds = 0.1): 
        self.__refreshRate = refreshRate
        self.__nextRefresh = 0
        
    def ready( self, context:EvaluationContext ) -> bool:
        if self.__nextRefresh >= context.when: return False
        
        self.__nextRefresh = context.when + self.__refreshRate
        return True

class Refreshable( object ):
    def __init__(self, refreshRate:TimeInSeconds = 0.1 ):
        self.__refreshCycle = RefreshCycle( refreshRate=refreshRate )
    
    @final
    def refresh( self, context:EvaluationContext):
        if self.__refreshCycle.ready(context):
            self.doRefresh(context)

    def doRefresh(self,context:EvaluationContext) -> None:
        raise NotImplemented



#############################################################################

class Evaluatable(Debuggable):
    
    def getValue(self, context:OptionalContextArg) -> Any:
        """ current value of term"""
        raise NotImplemented



def evaluate( value:Evaluatable|DirectValue, context:OptionalContextArg = None ):
    if isinstance( value, Evaluatable ):
        context = UpdateContext.fetchCurrentContext(context)
        if  context.debugEvaluate:
            with context.nestDebugEvaluate() as nde:
                rv = value.getValue(context)
                nde.say(value, "evaluate returning %r", rv)
            return rv
        else:
            return value.getValue(context)
    
    return value

     