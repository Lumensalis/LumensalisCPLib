from LumensalisCP.CPTyping import *
from LumensalisCP.common import *

import LumensalisCP.Main
from LumensalisCP.Main.Profiler import ProfileFrame, ProfileSubFrame, ProfileStubFrame


class UpdateContext(object):
    activeFrame: ProfileFrame
    
    _stubFrame = ProfileStubFrame( )
    
    def __init__( self, main:"LumensalisCP.Main.Manager.MainManager"=None ):
        #print( f"NEW UpdateContext @{id(self):X}")
        self.__updateIndex = 0
        self.__changedSources : List["LumensalisCP.Inputs.InputSource"] = []
        self.__mainRef = main.makeRef()
        self.__when = main.when
        self.activeFrame = None
        self.baseFrame = None

    @classmethod
    def _patch_fetchCurrentContext(cls, main:"LumensalisCP.Main.Manager.MainManager"):
        assert main is not None
        assert main._privateCurrentContext is not None
        def patchedFetchCurrentContext( context:"UpdateContext"|None ) -> "UpdateContext":
            return context or main._privateCurrentContext
        cls.fetchCurrentContext = patchedFetchCurrentContext
        
        
    def reset( self, when:TimeInMS|None = None ):
        try:
            self.__updateIndex += 1
            #self.__changedSources.clear()
            self.__when = when or self.main.when
            self.activeFrame = None
            self.baseFrame = None
        except Exception as inst:
            print( f"UpdateContext.refresh @{id(self):X} failed : {inst}")
            raise
        
    @property
    def main(self): return self.__mainRef()
        
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
        
    def addChangedSource( self, changed:"LumensalisCP.Inputs.InputSource"):
        #self.__changedSources.append( changed )
        pass
        
    def valueOf( self, value:Any ) -> Any:
        raise NotImplemented
    
        
    @staticmethod
    def fetchCurrentContext( context:"UpdateContext"|None ) -> "UpdateContext":
        """return context if it is not None, otherwise return the current
        context from the MainManager singleton

        :param context: the (potentially None) context to try first
        :type context: UpdateContext | None
        :return: the current context
        :rtype: UpdateContext
        """
        raise NotImplemented
        

#############################################################################

OptionalContextArg = Optional[UpdateContext]

#############################################################################
class RefreshCycle(object):
    def __init__(self, refreshRate:TimeInSeconds = 0.1): 
        self.__refreshRate = refreshRate
        self.__nextRefresh = 0
        
    def ready( self, context:UpdateContext ) -> bool:
        if self.__nextRefresh >= context.when: return False
        
        self.__nextRefresh = context.when + self.__refreshRate
        return True

class Refreshable( object ):
    def __init__(self, refreshRate:TimeInSeconds = 0.1 ):
        self.__refreshCycle = RefreshCycle( refreshRate=refreshRate )
    
    @final
    def refresh( self, context:UpdateContext):
        if self.__refreshCycle.ready(context):
            self.doRefresh(context)




#############################################################################

class Evaluatable(object):
    
    def getValue(self, context:OptionalContextArg):
        """ current value of term"""
        raise NotImplemented



def evaluate( value:Evaluatable|DirectValue, context:OptionalContextArg = None ):
    if isinstance( value, Evaluatable ):
        return value.getValue(fetchCurrentContext(context))
    
    return value

     