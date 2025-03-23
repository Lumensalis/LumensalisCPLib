from ..Identity.Local import NamedLocalIdentifiable
from LumensalisCP.CPTyping import Any, Callable, Generator, List, Mapping, Tuple
from LumensalisCP.CPTyping  import override
from LumensalisCP.common import dictAddUnique

class EvaluationContext(object):
    def __init__( self ):
        self.__updateIndex = 0
        
        
        self.__changedSources : List["InputSource"] = []
        
    def reset( self ):
        self.__updateIndex += 1
        self.__changedSources = []
        self.__changedTerms = []
        
    @property
    def updateIndex(self): return self.__updateIndex


    @property
    def changedSources(self): return self.__changedSources

    @property
    def changedTerms(self): return self.__changedTerms
    
    def addChangedTerm( self, changed:"ExpressionTerm"):
        self.__changedTerms.append( changed )
        
    def addChangedSource( self, changed:"InputSource"):
        self.__changedSources.append( changed )

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

class ExpressionTerm(object):
    def __init__(self):
        pass
    
        
    #def value(self, context:EvaluationContext) -> Any:
    def value(self, context:EvaluationContext):
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
    def value(self, context:EvaluationContext)  -> Any:
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
    def value(self, context:EvaluationContext) -> Any:
        return self.op( context, self.term.value( context ) )

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
    def value(self, context:EvaluationContext) -> Any:
        return self.op( context, self.term1.value( context ), self.term2.value( context ) )


class ExpressionConstant(ExpressionTerm):
    constantTypes = { int : True, bool: True, float: True, str: True }
    
    def __init__( self, value:Any=None ):
        super().__init__()
        assert self.constantTypes.get(type(value), True)
        self.__constantValue = value

    @override
    def value(self, context:EvaluationContext) -> Any:
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

class InputSource(NamedLocalIdentifiable, ExpressionTerm):

    def __init__(self, name):
        NamedLocalIdentifiable.__init__(self,name=name)
        ExpressionTerm.__init__(self)

        self.__latestValue = None
        self.__latestUpdate:int = None

    def getDerivedValue(self, context:EvaluationContext) -> Any:
        raise NotImplemented

    def updateValue(self, context:EvaluationContext) -> bool:
        val = self.getDerivedValue( context )
        self.__latestUpdate = context.updateIndex
        if val == self.__latestValue:
            return False
        if 0: print( f"value changing on {self.name} from {self.__latestValue} to {val} on update {context.updateIndex}" )
        self.__latestValue = val
        assert isinstance( context, EvaluationContext )
        context.addChangedSource( self )
        return True
        
            
    @override
    def value(self, context:EvaluationContext) -> Any:
        if self.__latestUpdate != context.updateIndex:
            self.updateValue( context )
        return self.__latestValue
    
    def path( self ): return None

#############################################################################

class OutputTarget(NamedLocalIdentifiable):

    def __init__(self, name:str = None):
        super().__init__(name=name)

    def set( self, value:Any, context:EvaluationContext ):
        raise NotImplemented

    def path( self ): return None
    
    
class CallbackSource( ExpressionTerm ):
    def __init__( self, name, callback  ):
        super().__init__()
        self.__name = name
        self.__callback = callback
        

    @override
    def value(self, context:EvaluationContext) -> Any:
        return self.__callback()
    
    
class Expression( object ):
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
    
    def sources( self ) -> Mapping[str,InputSource]:
        rv = {}
        for term in self.terms():
            if isinstance(term,InputSource):
                dictAddUnique( rv, term.name, term )

        return rv
    
    def updateValue(self, context:EvaluationContext ):
        term = self.term
        if self.whenClause is not None:
            whenResult = self.whenClause.value( context )
            if not whenResult:
                if self.otherwiseClause is not None:
                    term = self.otherwiseClause
                else:
                    return False
        value = term.value(context)
        if value == self.__latestValue:
            return False
        self.__latestValue = value
        context.addChangedTerm(term)
        return True
