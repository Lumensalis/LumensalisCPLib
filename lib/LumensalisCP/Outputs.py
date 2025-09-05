from LumensalisCP.ImportProfiler import  getImportProfiler
_sayOutputsImport = getImportProfiler( globals() ) # "Outputs"


from LumensalisCP.Eval.Expressions import *

#############################################################################

_sayOutputsImport.parsing()

class OutputTarget(CountedInstance, IDebuggable):

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
class NotifyingOutputTarget( OutputTarget, EvaluatableT[T], Generic[T] ):

    def __init__(self,onChange:Callable[[T,EvaluationContext], None],initialValue:Optional[T]=None) -> None:
        assert initialValue is not None, "NotifyingOutputTarget requires an initial value"
        self.__latestValue:T = initialValue
        self.onChange = onChange

    @property
    def latestValue(self) -> T | None:
        return self.__latestValue

    def set( self, value:T, context:EvaluationContext ) -> None:
        self.__latestValue = value
        self.onChange(value,context)

    def getValue(self, context:Optional[EvaluationContext]=None) -> T:
        return self.__latestValue
    
NotifyingOutputTargetT = GenericT(NotifyingOutputTarget)

#############################################################################

class NamedNotifyingOutputTarget(Generic[T],NotifyingOutputTargetT[T],NamedLocalIdentifiable):
    def __init__(self,
                 onChange:Callable[[T,EvaluationContext], None],initialValue:Optional[T]=None, 
                 **kwds:Unpack[NamedLocalIdentifiable.KWDS]
                 ) -> None:
        NotifyingOutputTargetT[T].__init__(self, onChange=onChange,initialValue=initialValue)
        NamedLocalIdentifiable.__init__(self, **kwds)

NamedNotifyingOutputTargetT = GenericT(NamedNotifyingOutputTarget)


#############################################################################
_NNOTD_SELF_T=TypeVar('_NNOTD_SELF_T' ) #, bound='Tunable')

class NamedNotifyingOutputTargetDescriptor(Generic[T,_NNOTD_SELF_T]):
    NOTIFIER_CLASS:ClassVar[type] = NamedNotifyingOutputTargetT[T]

    def __init__(self, 
                   name:str,
                   onChange:Callable[[_NNOTD_SELF_T,T,EvaluationContext], None],
                   initialValue:Optional[T]=None,
                   notifierClass:Optional[type]=None, 
                ) -> None:
        self.name:str = name
        self.onChange = onChange
        self.notifierClass:type = notifierClass or self.NOTIFIER_CLASS
        self.settingName = f"_nNotD_{name}"
        self.initialValue:T|None = initialValue

    def __makeNotifier(self, instance:_NNOTD_SELF_T) -> NamedNotifyingOutputTarget[T]:
        assert getattr(instance, self.settingName, None) is None
        onChange = self.onChange
        def changeWrap( value:T, context:EvaluationContext) -> None:
            onChange(instance, value, context)

        setting:NamedNotifyingOutputTarget[T] = \
                self.notifierClass( changeWrap, name=self.name, initialValue=self.initialValue )
        setattr(instance, self.settingName, setting)
        return setting

    def __getNotifier(self, instance:_NNOTD_SELF_T) -> NamedNotifyingOutputTarget[T]:
        setting = getattr(instance, self.settingName, None)
        if setting is None:
            setting = self.__makeNotifier(instance)
            #assert instance._tunableNotifiers.get(self.name) is setting
        return setting

    def __get__(self, instance:_NNOTD_SELF_T, owner:Any=None) -> NamedNotifyingOutputTarget[T]:
        #setting = getattr(instance, self.settingName, None)
        #if setting is None: return self.default
        setting = self.__getNotifier( instance )
        return setting

    def __set__(self, instance:_NNOTD_SELF_T, value:T) -> None:
        assert instance is not None,  f"Cannot set {self.name} "
        notifier =  self.__getNotifier( instance )
        notifier.set(value, UpdateContext.fetchCurrentContext(None))
        #setting.settingUpdate(value)

NamedNotifyingOutputTargetDescriptorT = GenericT(NamedNotifyingOutputTargetDescriptor)

_NNOTD_DESCRIPTOR_T=TypeVar('_NNOTD_DESCRIPTOR_T' )
#############################################################################

def notifyingOutputProperty(  default:T
            # descriptorClass:Type[_NNOTD_DESCRIPTOR_T],
            # **kwds:Unpack[TUNABLE_SETTING_KWDS[TUNABLE_T,TUNABLE_SELF_T]]
    ) -> Callable[ 
            [Callable[[Any,T,EvaluationContext],None]],
        NamedNotifyingOutputTargetDescriptor[T,Any]]:
    def decorated( onChange:Callable[
                        [Any, T, EvaluationContext], None] 
                ) -> NamedNotifyingOutputTargetDescriptor[T,Any]:



        descriptor = NamedNotifyingOutputTargetDescriptor(
                        name=onChange.__name__,
                        onChange=onChange,
                        initialValue=default,
                        #**kwds  # type: ignore
                    ) 
        return descriptor # type: ignore
    return decorated

notifyingOutputPropertyT = GenericT(notifyingOutputProperty)

#############################################################################
def notifyingBoolOutputProperty(  default:bool
    ) -> Callable[ 
            [Callable[[Any,bool,EvaluationContext],None]],
        NamedNotifyingOutputTargetDescriptor[bool,Any] ]:
    return  notifyingOutputProperty(  default )
    
#############################################################################
def notifyingPlusMinusOneOutputProperty(  default:PlusMinusOne
    ) -> Callable[ 
            [Callable[[Any,PlusMinusOne,EvaluationContext],None]],
        NamedNotifyingOutputTargetDescriptor[PlusMinusOne,Any] ]:
    return  notifyingOutputProperty(  default )
        
#############################################################################

_sayOutputsImport.complete(globals())
    
__all__ = [ 'OutputTarget', 'NamedOutputTarget',
           'NotifyingOutputTarget', 'NamedNotifyingOutputTarget',
            'NotifyingOutputTargetT', 'NamedNotifyingOutputTargetT',
            'notifyingOutputProperty',
            'notifyingBoolOutputProperty',
            'notifyingPlusMinusOneOutputProperty',

           ]
