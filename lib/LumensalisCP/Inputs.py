from LumensalisCP.Main.Expressions import *
from LumensalisCP.Identity.Local import NamedLocalIdentifiable

#############################################################################

class InputSource(NamedLocalIdentifiable, ExpressionTerm, Debuggable):

    def __init__(self, name:str = None):
        NamedLocalIdentifiable.__init__(self,name=name)
        ExpressionTerm.__init__(self)
        Debuggable.__init__(self)

        self.__latestValue = None
        self.__latestUpdateIndex:int = None
        self.__latestChangeIndex:int = None
        self.__onChangedList = []

    def __repr__( self ):
        return safeFmt( "%s:%s = %r", self.__class__.__name__, self.name, self.value )
    
    def getDerivedValue(self, context:UpdateContext) -> Any:
        raise NotImplemented
    
    def onChange(self, cb:Callable):
        self.__onChangedList.append(cb)

    def updateValue(self, context:UpdateContext) -> bool:
        assert isinstance( context, UpdateContext )
        if self.__latestChangeIndex == context.updateIndex:
            context.addChangedSource( self )
            return self.__latestValue
        
        val = self.getDerivedValue( context )
        self.__latestUpdateIndex = context.updateIndex
        if val == self.__latestValue:
            return False
        
        self.enableDbgOut and self.dbgOut( f"value changing on {self.name} from {self.__latestValue} to {val} on update {context.updateIndex}" )
        self.__latestValue = val
        self.__latestChangeIndex = context.updateIndex
        context.addChangedSource( self )
        for cb in self.__onChangedList:
            try:
                cb( source=self, context=context )
            except Exception as inst:
                self.SHOW_EXCEPTION( inst, "onChanged callback %r failed", cb )

        return True

    
    def cyclesSinceChange(self,context:UpdateContext) -> int:
        return UpdateContext.fetchCurrentContext(context)
                
    @property
    def value(self): return self.__latestValue
    
    def __bool__(self) -> bool:
        return bool(self.__latestValue)
    
    @override
    def getValue(self, context:EvaluationContext = None ) -> Any:
        if context is not None and self.__latestUpdateIndex != context.updateIndex:
            self.updateValue( context )
        return self.__latestValue
    
    def path( self ): return None

__all__ = [ InputSource ]