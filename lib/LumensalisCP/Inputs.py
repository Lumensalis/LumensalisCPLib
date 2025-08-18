from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayInputsImport = getImportProfiler( globals() ) # "Inputs"

#from LumensalisCP.common import *
from LumensalisCP.common import *
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.Main.Updates import UpdateContext

from LumensalisCP.Eval.Evaluatable import NamedEvaluatableProtocolT
from LumensalisCP.Eval.Expressions import ExpressionTerm    
from LumensalisCP.Eval.EvaluationContext import EvaluationContext
from LumensalisCP.CPTyping import Protocol
#############################################################################

_sayInputsImport.parsing()

class _InputSourceChangedCallback(Protocol):
    def __call__(self, source:InputSource, context:EvaluationContext) -> None:
        pass

class InputSource(NamedLocalIdentifiable, ExpressionTerm, NamedEvaluatableProtocolT[Any]):
    
    def __init__(self, **kwds:Unpack[NamedLocalIdentifiable.KWDS]) -> None:
        NamedLocalIdentifiable.__init__(self, **kwds)
        ExpressionTerm.__init__(self)
        
        self.__latestValue = None
        self.__latestUpdateIndex:int = -1
        self.__latestChangeIndex:int = -1
        self.__onChangedList:list[_InputSourceChangedCallback] = []

    def __repr__( self ):
        return safeFmt( "%s:%s = %r", self.__class__.__name__, self.name, self.value )
    
    @property
    def latestUpdateIndex(self) -> int:
        return self.__latestUpdateIndex
    @property
    def latestChangeIndex(self) -> int:
        return self.__latestChangeIndex
    @property
    def latestValue(self) -> Any:
        return self.__latestValue


    def expressionStrParts(self) -> Generator[str]:
        yield self.__class__.__name__ 
        yield ':'
        yield self.name 

    def getDerivedValue(self, context:EvaluationContext) -> Any:
        raise NotImplementedError
    
    def onChange(self, cb:_InputSourceChangedCallback) -> None:
        self.__onChangedList.append(cb)
    
    def removeOnChange(self, cb:_InputSourceChangedCallback) -> None:
        self.__onChangedList.remove(cb)

    def __callOnChanged(self, context:EvaluationContext): # pylint: disable=unused-private-member # type: ignore
        context.addChangedSource( self )
        if len( self.__onChangedList ) > 0:
            #with context.subFrame('InputSource.__callOnChanged', self.name) as frame:
            if True:    
                for cb in self.__onChangedList:
                    try:
                        cb( self, context )
                    except Exception as inst: # pylint: disable=broad-exception-caught
                        self.SHOW_EXCEPTION( inst, "onChanged callback %r failed", cb )

    def updateValue(self, context:EvaluationContext) -> bool:
        assert isinstance( context, EvaluationContext )
        if self.__latestChangeIndex == context.updateIndex:
            context.addChangedSource( self )
            return True

        #with context.subFrame('InputSource.updateValue', self.name) as frame:
        if True:
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
            #frame.snap( "__callOnChanged" )
            self.__callOnChanged(context)

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

_sayInputsImport.complete(globals())

__all__ = [ 'InputSource' ]
