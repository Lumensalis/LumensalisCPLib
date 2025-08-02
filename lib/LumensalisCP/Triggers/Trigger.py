from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__triggersSayImport = getImportProfiler( globals() ) # "Triggers.Trigger"
    

from LumensalisCP.IOContext import *
from LumensalisCP.Eval.Expressions import  Expression, ExpressionTerm #, UpdateContext
from LumensalisCP.util.kwCallback import KWCallback, KWCallbackArg # type: ignore
from LumensalisCP.Triggers.Invocable import *

#############################################################################
__triggersSayImport( "parsing... " )

#if TYPE_CHECKING:
#    from LumensalisCP.Eval.EvaluationContext import EvaluationContext
        
#TriggerActionType:TypeAlias = Invocable|Callable[[InputSource|None, EvaluationContext], None] # | KWCallbackArg
TriggerActionType:TypeAlias = Invocable
TriggerActionTypeArg:TypeAlias = Union[TriggerActionType, Callable[[EvaluationContext], None]]

class Trigger(NamedLocalIdentifiable, Invocable):
    """Triggers represent a set of actions that can be "fired" upon a condition being met
    
    Args:
        object (_type_): _description_
    """
    class KWDS(NamedLocalIdentifiable.KWDS):
        action:NotRequired[ Union[TriggerActionType, Callable[[EvaluationContext], None]]]

    def __init__( self, 
                 action:Optional[TriggerActionTypeArg] = None ,
                 **kwds:Unpack[NamedLocalIdentifiable.KWDS]
            ) -> None:
        name = kwds.get("name", None)
        if name is None and action is not None:
            name = (
                getattr(action, '__name__', None)
                  or getattr(action, 'name', None)
                  or getattr(action, 'tName', None)
                  or getattr(action, 'dbgName', None)
                    or f"{type(action).__name__}@{id(self):X}"
            )
            kwds['temporaryName'] = name
        
        super().__init__(**kwds)

        self.__actions:list[TriggerActionType] = []
        if action is not None:
            self.addAction(action)

    _onTrueExpression:Expression

    def addRawAction( self, action:TriggerActionType ) -> None:
        if self.enableDbgOut: self.dbgOut( "addAction( %r )", action )
        self.__actions.append( action )

    def addSimpleAction( self, action:InvocableSimpleCB ) -> None:
        if self.enableDbgOut: self.dbgOut( "addAction( %r )", action )
        #self.__actions.append( KWCallback.make( action ) )
        self.__actions.append( InvocableSimpleCB.make(action) )

    def addAction( self, action:TriggerActionTypeArg ) -> None:
        if self.enableDbgOut: self.dbgOut( "addAction( %r )", action )
        #self.__actions.append( KWCallback.make( action ) )

        self.__actions.append( Invocable.makeInvocable(action) )


    def fireTrigger(self, context:Optional[EvaluationContext] ) -> None:
        if context is None: context = UpdateContext.fetchCurrentContext(None)

        if self.enableDbgOut: 
            #self.dbgOut( f"firing timer {self.name}[{len(self.__actions)}]")
            with context.nestDebugEvaluate() as nde:
                nde.say(  self,  f"firing trigger on {self.__class__}@{hex(id(self))} [{len(self.__actions)}]" )
                for action in self.__actions:
                    nde.say( self, "firing action (%s) %r callable=%r",
                            action.__class__,
                            safeRepr(action),
                            callable(action)
                        )
                    try:
                        rv = action( context )
                        nde.say( "action returned %r", rv )

                    except Exception as inst: # pylint: disable=broad-exception-caught
                        #self.SHOW_EXCEPTION( inst, "firing action %s( %s )", action, kwds )
                        print ( f"Exception in action ({type(action).__name__}){action} : {inst!r}" )
                        self.SHOW_EXCEPTION( inst, "firing action %s", action )
        else:

            for action in self.__actions:
                try:
                    action( context )
                except Exception as inst: # pylint: disable=broad-exception-caught
                    #self.SHOW_EXCEPTION( inst, "firing action %s( %s )", action, kwds )
                    self.SHOW_EXCEPTION( inst, "firing action %s", action )

    def fireWithSource(self, source:Optional[InputSource], context:Optional[EvaluationContext] ) -> None:
        if context is None: context = UpdateContext.fetchCurrentContext(None)

        raise NotImplementedError("fireWithSource is not implemented")
        if self.enableDbgOut: 
            #self.dbgOut( f"firing timer {self.name}[{len(self.__actions)}]")
            with context.nestDebugEvaluate() as nde:
                nde.say(  self,  f"firing trigger on {self.__class__}@{hex(id(self))} [{len(self.__actions)}]" )
                for action in self.__actions:
                    nde.say( self, "firing action (%s) %r callable=%r",
                            action.__class__,
                            safeRepr(action),
                            callable(action)
                        )
                    try:
                        rv = action( source, context )
                        nde.say( "action returned %r", rv )

                    except Exception as inst: # pylint: disable=broad-exception-caught
                        #self.SHOW_EXCEPTION( inst, "firing action %s( %s )", action, kwds )
                        print ( f"Exception in action ({type(action).__name__}){action} : {inst!r}" )
                        self.SHOW_EXCEPTION( inst, "firing action %s", action )
        else:

            for action in self.__actions:
                try:
                    action( source, context )
                except Exception as inst: # pylint: disable=broad-exception-caught
                    #self.SHOW_EXCEPTION( inst, "firing action %s( %s )", action, kwds )
                    self.SHOW_EXCEPTION( inst, "firing action %s", action )

    def fireOnTrue( self, expression: Expression|ExpressionTerm ):
        if isinstance(expression,ExpressionTerm):
            expression = Expression(expression)

        self._onTrueExpression = expression
        def test( source:Optional[InputSource]=None, context:Optional[EvaluationContext] = None):
            context = UpdateContext.fetchCurrentContext(context)
            expression.updateValue(context)
            shouldFire = expression.value
            if self.enableDbgOut: self.dbgOut( "fireOnTrue shouldFire=%s", shouldFire)
            if shouldFire:
                self.fireTrigger( context )

        for source in expression.sources().values():
            source.onChange( test )
        
        return self

    def fireOnSourcesSet( self, *sources:InputSource):
        for source in sources:
            assert isinstance(source, InputSource )
            self.fireOnSet( source )

    def fireOnSet( self, source:InputSource):

        def test(source:Optional[InputSource]=None, context:Optional[EvaluationContext]=None) -> None: #
            context = UpdateContext.fetchCurrentContext(None)
            assert source is not None
            if source.getValue(context):
                if self.enableDbgOut: self.dbgOut( "firing on set of %s", source.name )
                self.fireWithSource(source, context)
            else:
                if self.enableDbgOut: self.dbgOut( "no fire on %s", source.name )
                
            
        source.onChange( test )
        return self

    def fireOnSetDef( self, source:Optional[InputSource]=None ):# -> Callable[..., Any]:
        assert source is not None
        self.fireOnSet( source )
        def on2( cb:TriggerActionType):# -> Any:
            self.addAction(cb)
            return cb
        return on2        
    
    
    def addActionDef( self, **kwds:StrAnyDict ): # pylint: disable=unused-argument
        def on2( cb:TriggerActionType ):
            self.addAction(cb)
            return cb
        return on2        

#############################################################################
__triggersSayImport.complete(globals())

__all__ = [
    'Trigger',
    'TriggerActionType',
 ]
