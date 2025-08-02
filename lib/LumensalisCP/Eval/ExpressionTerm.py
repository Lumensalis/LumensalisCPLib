from __future__ import annotations


from LumensalisCP.ImportProfiler import  getImportProfiler
_sayEvalExpressionTermImport = getImportProfiler( globals() ) # "Eval.ExpressionTerm"

from LumensalisCP.Lights.RGB import *
from LumensalisCP.Eval._common import *
from LumensalisCP.Eval.Evaluatable import Evaluatable

from LumensalisCP.Eval.EvaluationContext import EvaluationContext

if TYPE_CHECKING:
    #from LumensalisCP.Inputs import InputSource
    from LumensalisCP.Eval.Evaluatable import Evaluatable
    #from LumensalisCP.Inputs import InputSource
    
# TODO: tighten up type hints / lint
# pylint: disable=unused-argument,super-init-not-called
# pyright: reportUnusedVariable=false,reportUnusedFunction=false,reportUnusedClass=false
# pyright: reportUnknownParameterType=false,  reportUnknownVariableType=false
# pyright: reportMissingParameterType=false, reportMissingTypeArgument=false
# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false
# pyright: reportOperatorIssue=false


_sayEvalExpressionTermImport.parsing()

#############################################################################
EVAL_VALUE_TYPES:TypeAlias  = Union[ int, float, bool, str, RGB]

#############################################################################

class ExpressionOperationException( Exception ):
    def __init__( self, term:'ExpressionTerm', message:Optional[str]=None, inst:Optional[Exception]=None ):
        self.term = term
        self.inst = inst
        self.message = message
        messageParts = []
        try:
            if message is not None:
                messageParts.append(message)
                messageParts.append(" : ")    
            messageParts.append(term.__class__.__name__)
            messageParts.append(": ")
            messageParts.extend(term.expressionStrParts())
            if inst is not None:
                messageParts.append(" : ")
                messageParts.append(str(inst))
        except Exception as formatException: # pylint: disable=broad-exception-caught
            messageParts.append(" formatting exception:")
            messageParts.append(str(formatException))

        self.fullMessage = message = ''.join(messageParts)
        super().__init__(message)

#############################################################################



#############################################################################

class ExpressionTerm(Evaluatable): 
    class KWDS(TypedDict):
        pass

    def terms(self) -> Generator["ExpressionTerm"]:
        yield self
    
    def dependencies(self):  
        for term in self.terms():
            yield term

    def expressionStrParts(self) -> Generator[str]:
        raise NotImplementedError( 'expressionStrParts' )
        
    def expressionAsString(self) -> str:
        return ''.join( self.expressionStrParts())
        
    #def _makeTerm(self, other ):
    #    return other if isinstance( other, "ExpressionTerm" ) else makeExpressionConstant( other )
    
    def OR( self, other:Any ) -> "ExpressionTerm":         return makeBinaryOperation( self, TERM( other ), lambda c, a, b: a or b )
    def AND( self, other:Any )-> "ExpressionTerm":         return makeBinaryOperation( self, TERM( other ), lambda c, a, b: a and b )
    
    def __add__( self, other:Any )-> "ExpressionTerm":     return BinOp_add( self, other )
    def __sub__( self, other:Any ) -> "ExpressionTerm":    return BinOp_sub( self, other )
    def __mul__( self, other:Any ) -> "ExpressionTerm":    return BinOp_mul( self, other )
    def __truediv__( self, other:Any )-> "ExpressionTerm":    return BinOp_truediv( self, other )    
    
    def __floordiv__( self, other:Any )-> "ExpressionTerm":   return makeBinaryOperation( self, TERM( other ), lambda c, a, b: a // b )
    def __mod__( self, other:Any )-> "ExpressionTerm":        return makeBinaryOperation( self, TERM( other ), lambda c, a, b: a % b )
    def __divmod__( self, other:Any )-> "ExpressionTerm":    return makeBinaryOperation( self, TERM( other ), lambda c, a, b: divmod(a,b) )
    def __and__( self, other:Any ) -> "ExpressionTerm":     return makeBinaryOperation( self, other, lambda c, a, b: a and b )
    def __or__( self, other:Any ) -> "ExpressionTerm":      return makeBinaryOperation( self, other, lambda c, a, b: a or b )

    def __invert__( self )-> "ExpressionTerm":      return makeUnaryOperation( self, lambda c, a: ~a )
    
    def __radd__( self, other:Any ):         return makeBinaryOperation( self, TERM( other ), lambda c, b, a: a + b )
    def __rsub__( self, other:Any ) -> "ExpressionTerm":    return makeBinaryOperation( self, TERM( other ), lambda c, b, a: a - b )
    def __rmul__( self, other:Any ) -> "ExpressionTerm":    return makeBinaryOperation( self, TERM( other ), lambda c, b, a: a * b )
    def __rtruediv__( self, other:Any )-> "ExpressionTerm":    return makeBinaryOperation( self, TERM( other ), lambda c, b, a: a / b )
    def __rfloordiv__( self, other:Any )-> "ExpressionTerm":   return makeBinaryOperation( self, TERM( other ), lambda c, b, a: a // b )
    def __rmod__( self, other:Any )-> "ExpressionTerm":        return makeBinaryOperation( self, TERM( other ), lambda c, b, a: a % b )
    def __rdivmod__( self, other:Any )-> "ExpressionTerm":    return makeBinaryOperation( self, TERM( other ), lambda c, b, a: divmod(a,b) )
    def __rand__( self, other:Any ) -> "ExpressionTerm":     return makeBinaryOperation( self, other, lambda c, b, a: a and b )
    def __ror__( self, other:Any ) -> "ExpressionTerm":      return makeBinaryOperation( self, other, lambda c, b, a: a or b )

    def __lt__( self, other:Any )-> "ExpressionTerm": return makeBinaryOperation( self, other, lambda c, a, b: a < b )
    def __gt__( self, other:Any )-> "ExpressionTerm": return makeBinaryOperation( self, other, lambda c, a, b: a > b )
    def __eq__( self, other:Any )-> "ExpressionTerm": return makeBinaryOperation( self, other, lambda c, a, b: a == b ) # type: ignore
    def __ne__( self, other:Any )-> "ExpressionTerm": return makeBinaryOperation( self, other, lambda c, a, b: a != b ) # type: ignore
    def __le__( self, other:Any )-> "ExpressionTerm": return makeBinaryOperation( self, other, lambda c, a, b: a <= b )
    def __ge__( self, other:Any )-> "ExpressionTerm": return makeBinaryOperation( self, other, lambda c, a, b: a >= b )

    @override
    def getValue(self, context:Optional[EvaluationContext]=None)  -> EVAL_VALUE_TYPES:
        """ current value of term"""
        raise NotImplementedError( 'getValue' )

def ensureIsTerm( term:ExpressionTerm ) -> ExpressionTerm:
    assert isinstance( term, ExpressionTerm )
    return term

#############################################################################
class ExpressionOperation(ExpressionTerm): # pylint: disable=abstract-method
    pass

#############################################################################

class UnaryOperationBase(ExpressionOperation):
    OP_STRING = "???"
    
    def __init__(self, term:Any ):
        super().__init__()
        self.term = TERM(term)
    
    def expressionStrParts(self) -> Generator[str]:
        yield self.OP_STRING
        yield '('
        for p in self.term.expressionStrParts(): yield p
        yield ')'

    def terms(self) -> Generator["ExpressionTerm"]:
        for term in super().terms():
            yield term
        for child in self.term.terms():
            for t2 in child.terms():
                yield t2

    def calculate( self, context:EvaluationContext, a:Any ) ->Any: # pylint: disable=unused-argument
        raise NotImplementedError
        
    @override
    def getValue(self, context:Optional[EvaluationContext]=None) -> Any:
        context = UpdateContext.fetchCurrentContext(context)
        if context.debugEvaluate:
            with context.nestDebugEvaluate() as nde:
                v = self.term.getValue( context )
                rv = self.calculate( context, v )
                nde.say(self, "OP %r = %r", v, rv)
            return rv

        try:
            a = self.term.getValue( context )
            return  self.calculate( context, a ) 
        except Exception as inst:
            raise ExpressionOperationException( self, "getValue", inst=inst) from inst
        # pylint: disable=broad-exception-caught

#############################################################################

class UnaryOperation(UnaryOperationBase):
    def __init__(self, term:Any, op:Callable[[EvaluationContext,ExpressionTerm],Any] ) -> None:
        super().__init__(term)
        self.op = op
        
    @override
    def calculate( self, context:EvaluationContext, a:Any ) ->Any:
        return self.op( context, a  )
    
#############################################################################

class BinaryOperationBase(ExpressionOperation):
    OP_STRING = "???"
    def __init__(self, term1:ExpressionTerm, term2:Any ):
        super().__init__()
        self.term1 = ensureIsTerm(term1)
        self.term2 = ensureIsTerm(TERM(term2))

    def terms(self) -> Generator[ExpressionTerm]:
        for term in super().terms():
            yield term
        for child in self.term1.terms():
            for t2 in child.terms():
                yield t2
        for child in self.term2.terms():
            for t2 in child.terms():
                yield t2

    def expressionStrParts(self) -> Generator[str]:
        yield '('
        for p in self.term1.expressionStrParts(): yield p
        yield ')'
        yield self.OP_STRING
        yield '('
        for p in self.term2.expressionStrParts(): yield p
        yield ')'

    def calculate( self, context:EvaluationContext, a:EVAL_VALUE_TYPES, b:EVAL_VALUE_TYPES ) ->EVAL_VALUE_TYPES:  # pylint: disable=unused-argument
        raise NotImplementedError

    @override
    def getValue(self, context:Optional[EvaluationContext]=None) -> Any:
        if context is None: context = UpdateContext.fetchCurrentContext(context)
        if context.debugEvaluate:
            with context.nestDebugEvaluate() as nde:
                a = self.term1.getValue( context )
                b = self.term2.getValue( context )
                rv = self.calculate( context, a, b )
                nde.say(self, "%r OP %r = %r", a, b, rv)
            return rv
        
        try:
            a = self.term1.getValue( context )
            b = self.term2.getValue( context )
            return  self.calculate( context, a, b ) 
        except Exception as inst:
            raise ExpressionOperationException( self, "getValue", inst=inst) from inst
            
            #self.op( context, self.term1.getValue( context ), self.term2.getValue( context ) )

#############################################################################

class BinaryOperation(BinaryOperationBase):
    def __init__(self, term1:ExpressionTerm, term2:Any, op:Callable[[EvaluationContext,ExpressionTerm,ExpressionTerm], Any] ):
        super().__init__(term1, term2)
        self.op = op
        
    @override
    def calculate( self, context:EvaluationContext, a:Any, b:Any ) ->Any:
        return self.op( context, a, b )

#############################################################################

class BinOp_truediv(BinaryOperationBase):
    OP_STRING = "/"
    def calculate( self, context:EvaluationContext, a, b ): return a / b 


class BinOp_mul(BinaryOperationBase):
    OP_STRING = "*"
    def calculate( self, context:EvaluationContext, a, b ): return a * b 

class BinOp_add(BinaryOperationBase):
    OP_STRING = "+"
    def calculate( self, context:EvaluationContext, a, b ): return a + b 

class BinOp_sub(BinaryOperationBase):
    OP_STRING = "-"
    def calculate( self, context:EvaluationContext, a, b ): return a - b 
    
#############################################################################

class ExpressionConstant(ExpressionTerm):
    constantTypes = { int : True, bool: True, float: True, str: True }
    
    def __init__( self, value:Optional[Any]=None ):
        super().__init__()
        assert self.constantTypes.get(type(value), True)
        self.__constantValue = value

    def expressionStrParts(self) -> Generator[str]:
        yield str(self.__constantValue)
        
    @override
    def getValue(self, context:Optional[EvaluationContext]=None) -> Any:
        if context is None: context = UpdateContext.fetchCurrentContext(context)
        if context.debugEvaluate:
            self.infoOut( "(constant %r)", self.__constantValue)
        return self.__constantValue

#############################################################################

def TERM( value:Any ) -> ExpressionTerm :
    return value if isinstance( value, ExpressionTerm ) else makeExpressionConstant( value )

def NOT( value:Any ):
    return  makeUnaryOperation( TERM( value ), lambda c, a: not a ) 

def MAX( a:Any, b:Any ):
    return  makeBinaryOperation( TERM( a ), TERM( b ), lambda c, a, b: max(c.valueOf(a),c.valueOf(b)) ) 

def MIN( a:Any, b:Any ):
    return  makeBinaryOperation( TERM( a ), TERM( b ), lambda c, a, b: min(c.valueOf(a),c.valueOf(b)) ) 

#############################################################################

def makeExpressionConstant( value:Any ) -> ExpressionTerm: 
    return ExpressionConstant(value)

def makeBinaryOperation( term1:ExpressionTerm, term2:ExpressionTerm, op:Callable[[EvaluationContext,ExpressionTerm,ExpressionTerm]] ) -> ExpressionTerm:
    return BinaryOperation( term1=term1, term2=TERM(term2), op=op )

def makeUnaryOperation( term:ExpressionTerm, op:Callable[[EvaluationContext,ExpressionTerm]] )  -> ExpressionTerm:
    return UnaryOperation( term=TERM(term), op=op )

#############################################################################

class EdgeTerm(ExpressionOperation): # pylint: disable=abstract-method
    class KWDS(ExpressionOperation.KWDS):
        reset:NotRequired[ExpressionTerm]
        rising:NotRequired[bool]
        falling:NotRequired[bool]
        name:NotRequired[str]

    def __init__(self, term:ExpressionTerm,
                 reset:Optional[ExpressionTerm]=None,
                 rising:bool = False,  # pylint: disable=redefined-outer-name
                 falling:bool = False, # pylint: disable=redefined-outer-name
                 name:Optional[str]=None
                 ):
        super().__init__()
        self.name = name
        self.term = ensureIsTerm(term)
        self.__resetTerm = ensureIsTerm(reset) if reset is not None else None
        self.__awaitingReset = False
        assert rising or falling
        self.__latestUpdateIndex = 0
        self.__value = False
        self.__priorTermValue = None
        self.__onRising = rising
        self.__onFalling = falling
        
    def terms(self) -> Generator["ExpressionTerm"]:
        for term in super().terms():
            yield term
        for child in self.term.terms():
            for t2 in child.terms():
                yield t2
                
    def expressionStrParts(self) -> Generator[str]:
        
        yield 'Edge('
        if self.name is not None:
            yield 'name='
            yield repr(self.name)
        yield 'term='
        yield self.term.expressionAsString()
        yield ',rising='
        yield repr(self.__onRising)
        yield ',falling='
        yield repr(self.__onFalling)
        if self.__resetTerm is not None:
            yield ',reset='
            yield self.__resetTerm.expressionAsString()
        yield ')'

    @override
    def getValue(self, context:Optional[EvaluationContext] = None ) -> Any:
        assert context is not None
        if context is not None and self.__latestUpdateIndex != context.updateIndex: # type: ignore
            # priorUpdateIndex = self.__latestUpdateIndex
            self.__latestUpdateIndex = context.updateIndex
            
            #justReset = False
            if self.__awaitingReset:
                self.__value = False
                resetValue = self.__resetTerm.getValue( context ) if self.__resetTerm is not None else None
                if resetValue:
                    if self.enableDbgOut: self.dbgOut( "reset succeeded, value=%s at %s", self.__value, self.__latestUpdateIndex  )
                    self.__awaitingReset = False
                    
                return False
                
            termValue = self.term.getValue( context )
            if self.__priorTermValue is None or termValue != self.__priorTermValue:
                
                prior = self.__priorTermValue
                self.__priorTermValue = termValue 
                
                if termValue:
                    self.__value = self.__onRising
                else:
                    self.__value = self.__onFalling
                
                if self.__resetTerm is not None:
                    self.__awaitingReset = True
                    
                if self.enableDbgOut: self.dbgOut( "edge from %s to %s, value=%s at %s", prior, termValue, self.__value, self.__latestUpdateIndex  )
            else:
                if self.__value:
                    if self.enableDbgOut: self.dbgOut( "no edge term=%s at %s", termValue, self.__latestUpdateIndex  )
                self.__value = False
        return self.__value

def rising( term:Optional[ExpressionTerm]=None, **kwds:Unpack[EdgeTerm.KWDS] ) -> EdgeTerm:
    kwds.setdefault('rising', True)
    return EdgeTerm( term=TERM(term), **kwds )

def falling( term:Optional[ExpressionTerm]=None, **kwds:Unpack[EdgeTerm.KWDS] )  -> EdgeTerm:
    kwds.setdefault('falling', True)
    return EdgeTerm( term=TERM(term), **kwds )

#############################################################################


    
class CallbackSource( ExpressionTerm ):
    def __init__( self, name:str, callback  ): # pylint: disable=unused-argument
        super().__init__()
        self.__name = name
        self.__callback = callback
        
    def expressionStrParts(self) -> Generator[str]:
        yield 'CallbackSource('
        yield repr(self.__name)
        yield ','
        yield repr(self.__callback)
        yield ')'
        
    @override
    def getValue(self, context:Optional[EvaluationContext]=None) -> Any:
        return self.__callback()
    

#############################################################################

_sayEvalExpressionTermImport.complete(globals())
