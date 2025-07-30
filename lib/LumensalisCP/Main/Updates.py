from __future__ import annotations

from LumensalisCP.Main.PreMainConfig import pmc_getImportProfiler
_sayMainUpdatesImport = pmc_getImportProfiler( "Main.Updates" )


from LumensalisCP.CPTyping import *
from LumensalisCP.Debug import Debuggable
from LumensalisCP.common import *

from LumensalisCP.Main.Profiler import  ProfileFrameBase, ProfileSubFrame, ProfileStubFrame
from LumensalisCP.util.Releasable import Releasable

if TYPE_CHECKING:
    #import LumensalisCP.Main.Manager 
    from LumensalisCP.Main.Manager import MainManager
    from  LumensalisCP.Eval.Expressions import EvaluationContext
    from LumensalisCP.Inputs import InputSource
    from LumensalisCP.Lights.RGB import *

OptionalContextArg = Optional["EvaluationContext"]
DirectValue = Type[ Union[int,bool,float,'RGB' ] ]
    
# pylint: disable=protected-access
# pyright: ignore[reportPrivateUsage]

_sayMainUpdatesImport.parsing()

class UpdateContextDebugManager(Releasable):
    
    context:EvaluationContext|None
    
    def __init__( self ):
        super().__init__()
        #self.context:EvaluationContext|None = None
        self.debugEvaluate = True
        self.prior_debugEvaluate = False
        self.debugIndent = 0
        self.prior_debugIndent = -0

    def prepare( self, context:UpdateContext, debugEvaluate:bool = True ):
        self.context = context # type: ignore
        self.debugEvaluate = debugEvaluate

    def __enter__(self):
        assert self.context is not None
        self.prior_debugEvaluate = self.context.debugEvaluate
        self.prior_debugIndent = self.context._debugIndent # pyright: ignore[reportPrivateUsage]
        self.context.debugEvaluate = self.debugEvaluate
        self.context._debugIndent = self.debugIndent = self.prior_debugIndent + 2 # pyright: ignore[reportPrivateUsage]
        return self

    def __exit__(self, eT:Type[BaseException], eV:BaseException, eTB:Any):
        assert self.context is not None
        self.context.debugEvaluate = self.prior_debugEvaluate
        self.context._debugIndent = self.prior_debugIndent  # pyright: ignore[reportPrivateUsage]
        self.context = None

    def say( self, instanceOrMessage:Debuggable|str, *args:Any ) -> None:
        assert self.context is not None
        if isinstance(instanceOrMessage, str):
            message = instanceOrMessage
            instance = None
        else:
            assert isinstance( instanceOrMessage, Debuggable )
            instance = instanceOrMessage
            assert len(args) > 0
            message = args[0]
            assert isinstance(message, str)
            args = args[1:]
        if len(args)>0: message = safeFmt(message,*args)
            
        self.context.infoOut( "NDE %.32s %s %s",
                             "" if instance is None else instance.dbgName,
                              "                       "[:self.debugIndent],
                             message )

    def releaseNested(self):
        self.context = None
        
class UpdateContext(Debuggable):
    activeFrame: ProfileFrameBase
    
    def __init__( self, main:MainManager ):
        super().__init__()
        #print( f"NEW UpdateContext @{id(self):X}")
        self.__updateIndex = 0
        #self.__changedSources : list[InputSource] = []
        self.__mainRef = main.makeRef()
        self.__when = main.when
        #self.activeFrame = None
        self.baseFrame:ProfileFrameBase|None = None
        self.debugEvaluate = False
        self._debugIndent = 0
        self._stubFrame = ProfileStubFrame() # type: ignore[assignment]

    @classmethod
    def _patch_fetchCurrentContext(cls, main:MainManager):
        assert main is not None
        assert main._privateCurrentContext is not None # pyright: ignore[reportPrivateUsage]
        def patchedFetchCurrentContext( context:EvaluationContext|None ) -> EvaluationContext:
            return context or main._privateCurrentContext # pyright: ignore[reportPrivateUsage]
        cls.fetchCurrentContext = patchedFetchCurrentContext
        
    def nestDebugEvaluate(self, debugEvaluate:Optional[bool] = True ) -> UpdateContextDebugManager:
        entry = UpdateContextDebugManager.releasableGetInstance()
        entry.prepare( self,debugEvaluate if debugEvaluate is not None else self.debugEvaluate)
        return entry
    
    def reset( self, when:Optional[TimeInSeconds] = None ):
        try:
            self.__updateIndex += 1
            #self.__changedSources.clear()
            self.__when = when or self.main.when
            if hasattr(self, 'activeFrame'): del self.activeFrame 
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

    #@property
    #def changedSources(self): 
    #    raise NotImplementedError
    
    def subFrame(self, name:Optional[str]=None, name2:Optional[str]=None) -> ProfileSubFrame: # pylint: disable=unused-argument
        #rv = self.activeFrame.activeFrame().subFrame(self, name, name2)
        rv = self.activeFrame.subFrame(self, name, name2)
        return rv
    
    def stubFrame(self, name:Optional[str]=None, name2:Optional[str]=None) -> ProfileStubFrame: # pylint: disable=unused-argument
        return self._stubFrame
        
    def addChangedSource( self, changed:InputSource) -> None:
        #self.__changedSources.append( changed )
        pass
        
    def valueOf( self, value:Any ) -> Any:
        raise NotImplementedError
    
        
    @staticmethod
    def fetchCurrentContext( context:Optional[EvaluationContext]|None ) -> EvaluationContext:
        """return context if it is not None, otherwise return the current
        context from the MainManager singleton

        :param context: the (potentially None) context to try first
        :type context: UpdateContext | None
        :return: the current context
        :rtype: UpdateContext
        """
        raise NotImplementedError
        

#############################################################################
_sayMainUpdatesImport.complete(globals())

