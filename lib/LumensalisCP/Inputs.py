from LumensalisCP.Main.Expressions import *
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.common import safeFmt

if TYPE_CHECKING:
    pass
#############################################################################

class InputSource(NamedLocalIdentifiable, ExpressionTerm):

    def __init__(self, name:Optional[str] = None):
        NamedLocalIdentifiable.__init__(self,name=name)
        ExpressionTerm.__init__(self)
        
        self.__latestValue = None
        self.__latestUpdateIndex:int = -1
        self.__latestChangeIndex:int = -1
        self.__onChangedList = []

    def __repr__( self ):
        return safeFmt( "%s:%s = %r", self.__class__.__name__, self.name, self.value )
    
    def expressionStrParts(self) -> Generator[str]:
        yield( self.__class__.__name__ )
        yield(':')
        yield( self.name )

    def getDerivedValue(self, context:EvaluationContext) -> Any:
        raise NotImplementedError
    
    def onChange(self, cb:Callable):
        self.__onChangedList.append(cb)

    def __callOnChanged(self, context:EvaluationContext):
        context.addChangedSource( self )
        for cb in self.__onChangedList:
            try:
                cb( source=self, context=context )
            except Exception as inst:
                self.SHOW_EXCEPTION( inst, "onChanged callback %r failed", cb )

    def updateValue(self, context:EvaluationContext) -> bool:
        assert isinstance( context, EvaluationContext )
        if self.__latestChangeIndex == context.updateIndex:
            context.addChangedSource( self )
            return True

        if context.debugEvaluate:
            with context.nestDebugEvaluate() as nde:
                val = self.getDerivedValue( context )
                self.__latestUpdateIndex = context.updateIndex
                
                if val == self.__latestValue:
                    if self.enableDbgOut: self.dbgOut( "updateValue unchanged (%r) on update %d", self.__latestValue, context.updateIndex )
                    return False
                else:
                    nde.say( self, "value changing from %r to %r on %s", self.__latestValue, val, context.updateIndex )
        else:
            val = self.getDerivedValue( context )
            self.__latestUpdateIndex = context.updateIndex
            if val == self.__latestValue:
                return False
            if self.enableDbgOut: self.dbgOut( "updateValue changing from %r to %r on %s", self.__latestValue, val, context.updateIndex )
                
        self.__latestValue = val
        self.__latestChangeIndex = context.updateIndex

        return True

    
    def cyclesSinceChange(self,context:EvaluationContext) -> int:
        return UpdateContext.fetchCurrentContext(context).updateIndex - self.__latestChangeIndex
                
    @property
    def value(self): return self.__latestValue
    
    def __bool__(self) -> bool:
        return bool(self.__latestValue)
    
    @override
    def getValue(self, context:Optional[EvaluationContext] = None ) -> Any:
        if context is not None and self.__latestUpdateIndex != context.updateIndex:
            self.updateValue( context )
        return self.__latestValue
    
    def path( self ): return None

__all__ = [ 'InputSource' ]