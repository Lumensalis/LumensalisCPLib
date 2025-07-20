
from LumensalisCP.common import *

if TYPE_CHECKING:
    from  LumensalisCP.Eval.Expressions import EvaluationContext

#############################################################################
class RefreshCycle(object):
    def __init__(self, refreshRate:TimeInSeconds = 0.1): 
        self.__refreshRate = refreshRate
        self.__nextRefresh = 0
        
    def ready( self, context:'EvaluationContext' ) -> bool:
        if self.__nextRefresh >= context.when: return False
        
        self.__nextRefresh = context.when + self.__refreshRate
        return True

class Refreshable( object ):
    def __init__(self, refreshRate:TimeInSeconds = 0.1 ):
        self.__refreshCycle = RefreshCycle( refreshRate=refreshRate )
    
    @final
    def refresh( self, context:'EvaluationContext'):
        if self.__refreshCycle.ready(context):
            self.doRefresh(context)

    def doRefresh(self,context:'EvaluationContext') -> None:
        raise NotImplementedError
