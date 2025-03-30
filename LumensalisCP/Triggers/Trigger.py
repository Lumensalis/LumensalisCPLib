from LumensalisCP.CPTyping import *
from LumensalisCP.common import Debuggable
from LumensalisCP.Main.Expressions import InputSource, Expression, ExpressionTerm, UpdateContext

#############################################################################

class Trigger(Debuggable):
    """Triggers represent a set of actions that can be "fired" upon a condition being met
    
    Args:
        object (_type_): _description_
    """
    
    def __init__( self, name:str|None = None, action:Callable|None = None ):
        super().__init__()
        
        if name is None and action is not None:
            name = action.__name__
        self.__name = name
        self.__actions = []
        if action is not None:
            self.addAction(action)

    @property
    def name(self): return self.__name
    
    def addAction( self, action:Callable ):
        self.__actions.append( action )


    def fire(self, **kwds ):
        for action in self.__actions:
            action( **kwds )


    def fireOnTrue( self, expression: Expression|ExpressionTerm ):
        if isinstance(expression,ExpressionTerm):
            expression = Expression(expression)

        self._onTrueExpression = expression
        def test(source:InputSource=None, context:UpdateContext = None):
            
            expression.updateValue(context)
            shouldFire = expression.value
            self.dbgOut( "fireOnTrue shouldFire=%s", shouldFire)
            if shouldFire:
                self.fire()
            
        for source in expression.sources().values():
            source.onChange( test )
        
        return self


    def fireOnSet( self, source:InputSource):
        def test(source:InputSource=None, context:UpdateContext = None):
            if source.getValue(context):
                self.fire()
            
        source.onChange( test )
        return self

    def fireOnSetDef( self, source:InputSource=None ):
        assert source is not None
        self.fireOnSet( source )
        def on2( callable ):
            self.addAction(callable)
            return callable
        return on2        
    
#############################################################################
