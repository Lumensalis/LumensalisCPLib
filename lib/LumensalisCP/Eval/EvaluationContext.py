
from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayEvalEvaluationContextImport = getImportProfiler( globals() ) # "Eval.EvaluationContext"


from LumensalisCP.Eval._common import *
from LumensalisCP.Eval.Evaluatable import Evaluatable

if TYPE_CHECKING:
    #from LumensalisCP.Inputs import InputSource
    from LumensalisCP.Eval.ExpressionTerm import ExpressionTerm
    #from LumensalisCP.Inputs import InputSource


_sayEvalEvaluationContextImport.parsing()

_simpleValueTypes = set([int,bool,float])
    
class EvaluationContext(UpdateContext):    
    
        
    fetchCurrentContext = UpdateContext.fetchCurrentContext
    
    def addChangedTerm( self, changed:ExpressionTerm):
        pass
        # self.__changedTerms.append( changed )
        
    def valueOf( self, value:Any ) -> Any:
        if type(value)  in _simpleValueTypes:
            return value
        elif isinstance( value, Evaluatable ):
            term:Evaluatable[Any] = value # type: ignore[assignment]
            value = term.getValue( self )
        elif callable(value):
            value = self.valueOf( value() )
        return value        

_sayEvalEvaluationContextImport.complete(globals())
