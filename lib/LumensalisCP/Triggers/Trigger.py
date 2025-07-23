#from LumensalisCP.CPTyping import *
#from LumensalisCP.common import Debuggable
#from LumensalisCP.Inputs import InputSource
from LumensalisCP.IOContext import *
from LumensalisCP.Eval.Expressions import  Expression, ExpressionTerm #, UpdateContext

from LumensalisCP.util.kwCallback import KWCallback, KWCallbackArg

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

    _onTrueExpression:Expression
    
    @property
    def name(self): return self.__name
    
    def addAction( self, action:Callable ):
        if self.enableDbgOut: self.dbgOut( "addAction( %r )", action )
        self.__actions.append( KWCallback.make( action ) )


    def fire(self, **kwds ):
        if self.enableDbgOut: self.dbgOut( f"firing timer {self.name}[{len(self.__actions)}]")
        for action in self.__actions:
            try:
                action( **kwds )
            except Exception as inst: # pylint: disable=broad-exception-caught
                self.SHOW_EXCEPTION( inst, "firing action %s( %s )", action, kwds )

    def fireOnTrue( self, expression: Expression|ExpressionTerm ):
        if isinstance(expression,ExpressionTerm):
            expression = Expression(expression)

        self._onTrueExpression = expression
        def test(source:Optional[InputSource]=None, context:Optional[EvaluationContext] = None, **kwargs):
            context = UpdateContext.fetchCurrentContext(context)
            expression.updateValue(context)
            shouldFire = expression.value
            if self.enableDbgOut: self.dbgOut( "fireOnTrue shouldFire=%s", shouldFire)
            if shouldFire:
                self.fire(source=source, context=context, **kwargs)
            
        for source in expression.sources().values():
            source.onChange( test )
        
        return self

    def fireOnSourcesSet( self, *sources:InputSource):
        for source in sources:
            assert isinstance(source, InputSource )
            self.fireOnSet( source )

    def fireOnSet( self, source:InputSource):

        def test(source:Optional[InputSource]=None, context:Optional[EvaluationContext]=None, **kwargs):
            context = UpdateContext.fetchCurrentContext(None)
            assert source is not None
            if source.getValue(context):
                if self.enableDbgOut: self.dbgOut( "firing on set of %s", source.name )
                self.fire(source=source, context=context, **kwargs)
            else:
                if self.enableDbgOut: self.dbgOut( "no fire on %s", source.name )
                
            
        source.onChange( test )
        return self

    def fireOnSetDef( self, source:Optional[InputSource]=None ):
        assert source is not None
        self.fireOnSet( source )
        def on2( cb ):
            self.addAction(cb)
            return cb
        return on2        
    
    
    def addActionDef( self, **kwds ): # pylint: disable=unused-argument
        def on2( cb ):
            self.addAction(cb)
            return cb
        return on2        

#############################################################################
