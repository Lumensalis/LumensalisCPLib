#import LumensalisCP.Inputs
import LumensalisCP.Main
from ..Identity.Local import NamedLocalIdentifiable
from LumensalisCP.CPTyping import Any, Callable, Generator, List, Mapping, Tuple
from LumensalisCP.CPTyping  import override
from LumensalisCP.common import *
from .Updates import UpdateContext, RefreshCycle
from LumensalisCP.Main.Profiler import Profiler, ProfileFrame


class EvaluationContext(UpdateContext):
    
    def __init__( self, *args, **kwds ):
        super().__init__( *args, **kwds )
        self.__updateIndex = 0
        
        
        self.__changedTerms : List["ExpressionTerm"] = []
        
    def reset( self ):
        super().reset()
        self.__changedTerms = []
    
    @property
    def updateIndex(self) -> int: 
        return self.__updateIndex
    
    @property
    def changedTerms(self) -> List["ExpressionTerm"]:
        return self.__changedTerms
    
    def addChangedTerm( self, changed:"ExpressionTerm"):
        self.__changedTerms.append( changed )
        
    def valueOf( self, value:Any ) -> Any:
        #xm : 'LumensalisCP.Main.Expressions'
        #xm = Expressions #LumensalisCP.Main.Expressions
          
        if type(value) is object:
            if isinstance( value, ExpressionTerm ):
                term = value
                value = term.getValue( self )
                print( f"valueOf term {term} = {value}")
            elif isinstance( value, Expression ):
                value.updateValue( self )
                value = value.value
                print( f"valueOf Expression {term} = {value}")
            elif callable(value):
                value = self.valueOf(value())
        elif isinstance( value, ExpressionTerm ):
            term = value
            value = term.getValue( self )
            #print( f"valueOf term ({type(term)}) {term} = {value}")
        
        elif callable(value):
            value = self.valueOf( value() )
        return value        


#############################################################################
class Evaluatable(object):
    
    def getValue(self, context:EvaluationContext):
        # type: (EvaluationContext) -> Any
        """ current value of term"""
        raise NotImplemented
    
#############################################################################

def makeExpressionConstant(value:Any=None) -> "ExpressionTerm" : 
    raise NotImplemented

def makeBinaryOperation( term1:"ExpressionTerm"=None, term2:"ExpressionTerm"=None, op:Callable[[EvaluationContext,"ExpressionTerm","ExpressionTerm"]] =None ) -> "ExpressionTerm":
    raise NotImplemented

def makeUnaryOperation( term:"ExpressionTerm"=None, op:Callable[[EvaluationContext,"ExpressionTerm"]] =None)  -> "ExpressionTerm":
    raise NotImplemented

def TERM( value:Any ) -> "ExpressionTerm" :
    raise NotImplemented

def ensureIsTerm( term:"ExpressionTerm" ) -> "ExpressionTerm" :
    raise NotImplemented

#############################################################################

class ExpressionTerm(Evaluatable):
    def __init__(self):
        pass
    
        
    #def value(self, context:EvaluationContext) -> Any:
    def getValue(self, context:EvaluationContext):
        # type: (EvaluationContext) -> Any
        """ current value of term"""
        raise NotImplemented
    

    def terms(self) -> Generator["ExpressionTerm"]:
        yield self
        
    #def _makeTerm(self, other ):
    #    return other if isinstance( other, "ExpressionTerm" ) else makeExpressionConstant( other )
    
    def OR( self, other:Any ) -> "ExpressionTerm":         return makeBinaryOperation( self, TERM( other ), lambda c, a, b: a or b )
    def AND( self, other:Any )-> "ExpressionTerm":         return makeBinaryOperation( self, TERM( other ), lambda c, a, b: a and b )
    
    def __add__( self, other:Any )-> "ExpressionTerm":         return makeBinaryOperation( self, TERM( other ), lambda c, a, b: a + b )
    def __sub__( self, other:Any ) -> "ExpressionTerm":    return makeBinaryOperation( self, TERM( other ), lambda c, a, b: a - b )
    def __mul__( self, other:Any ) -> "ExpressionTerm":    return makeBinaryOperation( self, TERM( other ), lambda c, a, b: a * b )
    def __truediv__( self, other:Any )-> "ExpressionTerm":    return makeBinaryOperation( self, TERM( other ), lambda c, a, b: a / b )
    def __floordiv__( self, other:Any )-> "ExpressionTerm":   return makeBinaryOperation( self, TERM( other ), lambda c, a, b: a // b )
    def __mod__( self, other:Any )-> "ExpressionTerm":        return makeBinaryOperation( self, TERM( other ), lambda c, a, b: a % b )
    def __divmod__( self, other:Any )-> "ExpressionTerm":    return makeBinaryOperation( self, TERM( other ), lambda c, a, b: divmod(a,b) )
    def __and__( self, other ) -> "ExpressionTerm":     return makeBinaryOperation( self, other, lambda c, a, b: a and b )
    def __or__( self, other ) -> "ExpressionTerm":      return makeBinaryOperation( self, other, lambda c, a, b: a or b )

    def __invert__( self )-> "ExpressionTerm":      return makeUnaryOperation( self, lambda c, a: ~a )
    
    def __radd__( self, other:Any ):         return makeBinaryOperation( self, TERM( other ), lambda c, b, a: a + b )
    def __rsub__( self, other:Any ) -> "ExpressionTerm":    return makeBinaryOperation( self, TERM( other ), lambda c, b, a: a - b )
    def __rmul__( self, other:Any ) -> "ExpressionTerm":    return makeBinaryOperation( self, TERM( other ), lambda c, b, a: a * b )
    def __rtruediv__( self, other:Any )-> "ExpressionTerm":    return makeBinaryOperation( self, TERM( other ), lambda c, b, a: a / b )
    def __rfloordiv__( self, other:Any )-> "ExpressionTerm":   return makeBinaryOperation( self, TERM( other ), lambda c, b, a: a // b )
    def __rmod__( self, other:Any )-> "ExpressionTerm":        return makeBinaryOperation( self, TERM( other ), lambda c, b, a: a % b )
    def __rdivmod__( self, other:Any )-> "ExpressionTerm":    return makeBinaryOperation( self, TERM( other ), lambda c, b, a: divmod(a,b) )
    def __rand__( self, other ) -> "ExpressionTerm":     return makeBinaryOperation( self, other, lambda c, b, a: a and b )
    def __ror__( self, other ) -> "ExpressionTerm":      return makeBinaryOperation( self, other, lambda c, b, a: a or b )

    def __lt__( self, other:Any )-> "ExpressionTerm": return makeBinaryOperation( self, other, lambda c, a, b: a < b )
    def __gt__( self, other:Any )-> "ExpressionTerm": return makeBinaryOperation( self, other, lambda c, a, b: a > b )
    def __eq__( self, other:Any )-> "ExpressionTerm": return makeBinaryOperation( self, other, lambda c, a, b: a == b )
    def __ne__( self, other:Any )-> "ExpressionTerm": return makeBinaryOperation( self, other, lambda c, a, b: a != b )
    def __le__( self, other:Any )-> "ExpressionTerm": return makeBinaryOperation( self, other, lambda c, a, b: a <= b )
    def __ge__( self, other:Any )-> "ExpressionTerm": return makeBinaryOperation( self, other, lambda c, a, b: a >= b )

    @override
    def getValue(self, context:EvaluationContext)  -> Any:
        """ current value of term"""
        pass



def ensureIsTerm( term:ExpressionTerm ) -> ExpressionTerm:
    assert isinstance( term, ExpressionTerm )
    return term

#############################################################################
class ExpressionOperation(ExpressionTerm):
    
    def __init__(self):
        super().__init__()

#############################################################################

class UnaryOperation(ExpressionOperation):
    def __init__(self, term:ExpressionTerm=None, op:Callable[[EvaluationContext,ExpressionTerm]]=None ):
        super().__init__()
        self.term = ensureIsTerm(term)
        self.op = op

    def terms(self) -> Generator["ExpressionTerm"]:
        for term in super().terms():
            yield term
        for child in self.term.terms():
            for t2 in child.terms():
                yield t2

    @override
    def getValue(self, context:EvaluationContext) -> Any:
        return self.op( context, self.term.getValue( context ) )

class BinaryOperation(ExpressionOperation):
    def __init__(self, term1:ExpressionTerm=None, term2:ExpressionTerm=None, op:Callable[[EvaluationContext,ExpressionTerm,ExpressionTerm]]=None ):
        super().__init__()
        self.op = op
        self.term1 = ensureIsTerm(term1)
        self.term2 = ensureIsTerm(term2)

    def terms(self) -> Generator["ExpressionTerm"]:
        for term in super().terms():
            yield term
        for child in self.term1.terms():
            for t2 in child.terms():
                yield t2
        for child in self.term2.terms():
            for t2 in child.terms():
                yield t2

    @override
    def getValue(self, context:EvaluationContext) -> Any:
        return self.op( context, self.term1.getValue( context ), self.term2.getValue( context ) )


class ExpressionConstant(ExpressionTerm):
    constantTypes = { int : True, bool: True, float: True, str: True }
    
    def __init__( self, value:Any=None ):
        super().__init__()
        assert self.constantTypes.get(type(value), True)
        self.__constantValue = value

    @override
    def getValue(self, context:EvaluationContext) -> Any:
        return self.__constantValue
    
    
def TERM( value:Any ) -> ExpressionTerm :
    return value if isinstance( value, ExpressionTerm ) else makeExpressionConstant( value )

def NOT( value:Any ):
    return  makeUnaryOperation( TERM( value ), lambda c, a: not a ) 


#############################################################################

def makeExpressionConstant(value:Any=None) -> ExpressionTerm: 
    return ExpressionConstant(value)

def makeBinaryOperation( term1:ExpressionTerm=None, term2:ExpressionTerm=None, op:Callable[[EvaluationContext,ExpressionTerm,ExpressionTerm]]=None ) -> ExpressionTerm:
    return BinaryOperation( term1=term1, term2=TERM(term2), op=op )

def makeUnaryOperation( term:ExpressionTerm=None, op:Callable[[EvaluationContext,ExpressionTerm]]=None )  -> ExpressionTerm:
    return UnaryOperation( term=TERM(term), op=op )

#############################################################################

class EdgeTerm(ExpressionOperation,Debuggable):
    def __init__(self, term:ExpressionTerm=None,
                 reset:ExpressionTerm=None,
                 rising:bool = False,
                 falling:bool = False,
                 name:str=None
                 ):
        super().__init__()
        Debuggable.__init__(self)
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

    @override
    def getValue(self, context:EvaluationContext = None ) -> Any:
        assert context is not None
        if context is not None and self.__latestUpdateIndex != context.updateIndex:
            priorUpdateIndex = self.__latestUpdateIndex
            self.__latestUpdateIndex = context.updateIndex
            
            #justReset = False
            if self.__awaitingReset:
                self.__value = False
                resetValue = self.__resetTerm.getValue( context )
                if resetValue:
                    self.dbgOut( "reset succeeded, value=%s at %s", self.__value, self.__latestUpdateIndex  )
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
                    
                self.dbgOut( "edge from %s to %s, value=%s at %s", prior, termValue, self.__value, self.__latestUpdateIndex  )
            else:
                if self.__value != False:
                    self.dbgOut( "no edge term=%s at %s", termValue, self.__latestUpdateIndex  )
                self.__value = False
        return self.__value

def rising( term:ExpressionTerm=None, **kwds ) -> EdgeTerm:
    return EdgeTerm( term=TERM(term), rising=True, **kwds )

def falling( term:ExpressionTerm=None, **kwds )  -> EdgeTerm:
    return EdgeTerm( term=TERM(term), falling=True, **kwds )

#############################################################################


    
class CallbackSource( ExpressionTerm ):
    def __init__( self, name, callback  ):
        super().__init__()
        self.__name = name
        self.__callback = callback
        

    @override
    def getValue(self, context:EvaluationContext) -> Any:
        return self.__callback()
    



#############################################################################

class Expression( Evaluatable ):
    def __init__( self, term:ExpressionTerm ):
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
    def term(self): return self.__root
    
    @property
    def whenClause(self): return self.__when
    
    @property
    def otherwiseClause(self): return self.__otherwise
    
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
    
    def sources( self ) -> Mapping[str,"LumensalisCP.Inputs.InputSource"]:
        rv = {}
        for term in self.terms():
            if isinstance(term,LumensalisCP.Inputs.InputSource):
                dictAddUnique( rv, term.name, term )

        return rv
    
    def getValue(self, context:EvaluationContext ):
        self.updateValue(context)
        return self.__latestValue
    
    def updateValue(self, context:EvaluationContext ):
        term = self.term
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
