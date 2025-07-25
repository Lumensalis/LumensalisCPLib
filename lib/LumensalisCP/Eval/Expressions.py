from __future__ import annotations

from LumensalisCP.Eval._common import *
from LumensalisCP.Eval.Evaluatable import Evaluatable
from LumensalisCP.Eval.EvaluationContext import EvaluationContext
from LumensalisCP.Eval.ExpressionTerm import ExpressionTerm, ensureIsTerm

if TYPE_CHECKING:
    #from LumensalisCP.Inputs import InputSource
    from LumensalisCP.Eval.Evaluatable import Evaluatable
    from LumensalisCP.Inputs import InputSource
    
    
# TODO: tighten up type hints / lint
# pylint: disable=unused-argument,super-init-not-called
# pyright: reportUnusedVariable=false,reportUnusedFunction=false,reportUnusedClass=false
# pyright: reportUnknownParameterType=false,  reportUnknownVariableType=false
# pyright: reportMissingParameterType=false, reportMissingTypeArgument=false
# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false
# pyright: reportOperatorIssue=false

#############################################################################


#############################################################################

class Expression( Evaluatable ):
    def __init__( self, term:ExpressionTerm ):
        super().__init__()
        self.__root = ensureIsTerm(term)
        self.__when:ExpressionTerm|None = None
        self.__otherwise:ExpressionTerm|None = None
        self.__latestValue:Any = None


    def terms(self) -> Generator[ExpressionTerm]:
        
        for term in (self.__root, self.__when, self.__otherwise):
            if term is not None:
                for t2  in term.terms():
                    yield t2

    @property
    def value(self): return self.__latestValue
    
    @property
    def term(self) -> ExpressionTerm: return self.__root
    
    @property
    def whenClause(self) -> ExpressionTerm | None: return self.__when
    
    @property
    def otherwiseClause(self) -> ExpressionTerm | None: return self.__otherwise
    
    def when(self, condition:ExpressionTerm ) -> "Expression":
        ensureIsTerm( condition )
        assert self.__when is None
        self.__when = condition
        return self
    
    def otherwise(self, condition:ExpressionTerm ) -> "Expression":
        ensureIsTerm( condition )
        assert self.__otherwise is None
        self.__otherwise = condition
        return self
    
    def sources( self ) -> dict[str,InputSource]:
        rv = {}
        for term in self.terms():
            if isinstance(term,LumensalisCP.Inputs.InputSource): # type: ignore
                dictAddUnique( rv, term.name, term ) # type: ignore

        return rv
    
    def getValue(self, context:Optional[EvaluationContext]=None ):
        self.updateValue(UpdateContext.fetchCurrentContext(context))
        return self.__latestValue
    
    def updateValue(self, context:EvaluationContext ) -> bool:
        term = self.term
        assert term is not None
        if self.whenClause is not None:
            whenResult = self.whenClause.getValue( context )
            if not whenResult:
                if self.otherwiseClause is not None:
                    term = self.otherwiseClause
                else:
                    return False
        value = term.getValue(context)
        if value == self.__latestValue:
            return False
        self.__latestValue = value
        context.addChangedTerm(term)
        return True
