
from __future__ import annotations

from LumensalisCP.Main.PreMainConfig import ImportProfiler
_sayEvalEvaluationContextImport = ImportProfiler( "Eval.EvaluationContext" )


from LumensalisCP.Eval._common import *
from LumensalisCP.Eval.Evaluatable import Evaluatable

if TYPE_CHECKING:
    #from LumensalisCP.Inputs import InputSource
    from LumensalisCP.Eval.ExpressionTerm import ExpressionTerm
    #from LumensalisCP.Inputs import InputSource
    

_sayEvalEvaluationContextImport.parsing()

_simpleValueTypes = set([int,bool,float])
    
class EvaluationContext(UpdateContext):    
    
    #def __init__( self, *args, **kwds ):
        #super().__init__( *args, **kwds)
        #self.__changedTerms : List["ExpressionTerm"] = []
        
    fetchCurrentContext = UpdateContext.fetchCurrentContext
    
    def reset( self, when:TimeInSeconds|None = None ):
        UpdateContext.reset(self,when)
        #self.__changedTerms.clear()
    
    # @property
    #def changedTerms(self) -> List["ExpressionTerm"]:
    #    return self.__changedTerms
    
    def addChangedTerm( self, changed:ExpressionTerm):
        pass
        # self.__changedTerms.append( changed )
        
    def valueOf( self, value:Any ) -> Any:
        if type(value)  in _simpleValueTypes:
            return value
        elif isinstance( value, Evaluatable ):
            term = value
            value = term.getValue( self )
        elif callable(value):
            value = self.valueOf( value() )
        return value        

_sayEvalEvaluationContextImport.complete()
