
from LumensalisCP.ImportProfiler import  getImportProfiler
_sayOutputsImport = getImportProfiler( globals() ) # "Outputs"


from LumensalisCP.Eval.Expressions import *

#############################################################################

_sayOutputsImport.parsing()

class OutputTarget(CountedInstance):

    def __init__(self, name:Optional[str] = None):
        super().__init__()
        
    def set( self, value:Any, context:EvaluationContext ) -> None:
        raise NotImplementedError
    
    
class NamedOutputTarget(NamedLocalIdentifiable,OutputTarget):

    def __init__(self, **kwds:Unpack[NamedLocalIdentifiable.KWDS]):
        NamedLocalIdentifiable.__init__(self,**kwds)
        OutputTarget.__init__(self)

    @override
    def set( self, value:Any, context:EvaluationContext ) -> None:
        raise NotImplementedError

    def path( self ): return None

#############################################################################
T=TypeVar('T')  
class NotifyingOutputTarget( OutputTarget, Generic[T] ):

    def __init__(self,onChange:Callable[[EvaluationContext,T], None],initialValue:Optional[T]=None) -> None:
        self.__latestValue:T|None = initialValue
        self.onChange = onChange

    @property
    def latestValue(self) -> T | None:
        return self.__latestValue

    def set( self, value:T, context:EvaluationContext ) -> None:
        self.__latestValue = value
        self.onChange(context,value)

NotifyingOutputTargetT = GenericT(NotifyingOutputTarget)

class NamedNotifyingOutputTarget(Generic[T],NotifyingOutputTargetT[T],NamedLocalIdentifiable):
    def __init__(self,
                 onChange:Callable[[EvaluationContext,T], None],initialValue:Optional[T]=None, 
                 **kwds:Unpack[NamedLocalIdentifiable.KWDS]
                 ) -> None:
        NotifyingOutputTargetT[T].__init__(self, onChange=onChange,initialValue=initialValue)
        NamedLocalIdentifiable.__init__(self, **kwds)

NamedNotifyingOutputTargetT = GenericT(NamedNotifyingOutputTarget)

#############################################################################

_sayOutputsImport.complete(globals())
    
__all__ = [ 'OutputTarget', 'NamedOutputTarget',
           'NotifyingOutputTarget', 'NamedNotifyingOutputTarget',
            'NotifyingOutputTargetT', 'NamedNotifyingOutputTargetT'
           ]
