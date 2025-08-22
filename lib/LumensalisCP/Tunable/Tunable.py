from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__profileImport = getImportProfiler( globals() ) # "Outputs"

# pyright: reportUnusedImport=false, reportPrivateUsage=false

from LumensalisCP.Eval.Expressions import *
from LumensalisCP.Eval.ExpressionTerm  import ExpressionTerm,  EVAL_VALUE_TYPES
from LumensalisCP.Outputs import NamedNotifyingOutputTarget, NotifyingOutputTargetT,OutputTarget
from LumensalisCP.Interactable.Interactable import Interactable, InteractableT, INTERACTABLE_ARG_T, INTERACTABLE_T

from LumensalisCP.Tunable.TunableKWDS import *
#############################################################################

__profileImport.parsing()

#############################################################################
TUNABLE_SELF_T=TypeVar('TUNABLE_SELF_T', bound='Tunable')


class TunableSetting(NamedLocalIdentifiable,OutputTarget,
                     InteractableT[TUNABLE_T],
                     ExpressionTerm,
                     Generic[ TUNABLE_T,TUNABLE_SELF_T]):

    TUNABLE_DEFAULTS:ClassVar[StrAnyDict] = {}

    def __init__(self, tunable:TUNABLE_SELF_T, **kwargs:Unpack[TUNABLE_SETTING_KWDS[TUNABLE_T,TUNABLE_SELF_T]]) -> None:
        for key,val in self.TUNABLE_DEFAULTS.items():
            kwargs.setdefault(key, val) # type: ignore

        value = kwargs.get('startingValue', None)
        assert value is not None, "TunableSetting must have a startingValue"

        self.onChange:Callable[[TUNABLE_SELF_T, TunableSetting[ TUNABLE_T,TUNABLE_SELF_T], 
                                EvaluationContext], None]|None = kwargs.pop('onChange', None) # type: ignore
        
        if self.onChange is None:
            self.warnOut("TunableSetting has no onChange handler %r", kwargs )

        self.__tunable = weakref.ref(tunable)
        kwargs,nliArgs = NamedLocalIdentifiable.extractInitArgs(kwargs)
        NamedLocalIdentifiable.__init__(self, **nliArgs)
        InteractableT[TUNABLE_T].__init__(self, **kwargs) # type: ignore
        EvaluatableT[TUNABLE_T].__init__(self)

        self.__value:TUNABLE_T = value # type: ignore

    def set( self, value:Any, context:EvaluationContext ) -> None:
        self.infoOut( "set (OutputTarget) to %s", value)
        # from OutputTarget
        self.settingUpdate(value, context)

    def settingUpdate( self, value:TUNABLE_T, context:Optional[EvaluationContext]=None ) -> None:
        try:
            if self.enableDbgOut: self.dbgOut("settingUpdate : %s", value)
            v = self.interactConvert(value)
            if v == self.__value:
                if self.enableDbgOut: self.dbgOut("settingUpdate no change: %s", v)
                return
            self.__value = v
            if self.enableDbgOut: self.dbgOut("settingUpdate changed: %s", v)

            if context is None:
                context = UpdateContext.fetchCurrentContext(context)

            if self.onChange:
                if self.enableDbgOut: self.dbgOut("settingUpdate onChange...")

                self.onChange(self.__tunable(), self, context) # type: ignore
        except Exception as e:
            self.SHOW_EXCEPTION( e, "settingUpdate %s error", value )
            raise
            

    @property
    def value(self) -> TUNABLE_T:
        return self.__value
    
    def getValue(self, context:Optional[EvaluationContext]=None)  -> EVAL_VALUE_TYPES:
        """ current value of term"""
        return self.__value
    def __call__(self, context:Optional[EvaluationContext]=None) -> TUNABLE_T:
        return self.__value
    
TunableSettingT = GenericT(TunableSetting)


#############################################################################
class TunableDescriptor(Generic[TUNABLE_T,TUNABLE_SELF_T]):
    SETTING_CLASS:ClassVar[type]

    def __init__(self, settingClass:Optional[type]=None, 
                 **settingKwds:Unpack[TUNABLE_SETTING_KWDS[TUNABLE_T,TUNABLE_SELF_T]] # type: ignore
                 ) -> None:
        name = settingKwds.get('name', None)
        default = settingKwds.get('startingValue', None)
        assert name is not None and default is not None, "TunableDescriptor must have a name and default value"
        self.name = name
        self.settingClass = settingClass or self.SETTING_CLASS
        self.settingName = f"_ts_{name}"
        self.default:TUNABLE_T = default # type: ignore
        self._settingKwds:TUNABLE_SETTING_KWDS[TUNABLE_T,TUNABLE_SELF_T] = settingKwds 

    def __makeSetting(self, instance:TUNABLE_SELF_T) -> TunableSetting[TUNABLE_T,TUNABLE_SELF_T]:
        assert getattr(instance, self.settingName, None) is None
        # need to copy because constructor mutates kwargs
        settings:TUNABLE_SETTING_KWDS[TUNABLE_T,TUNABLE_SELF_T] = dict(self._settingKwds) # type: ignore

        setting:TunableSetting[TUNABLE_T,TUNABLE_SELF_T] = \
                                self.settingClass( instance, **settings )
        setattr(instance, self.settingName, setting)
        return setting

    def __getSetting(self, instance:TUNABLE_SELF_T) -> TunableSetting[TUNABLE_T,TUNABLE_SELF_T]:
        setting = getattr(instance, self.settingName, None)
        if setting is None:
            setting = self.__makeSetting(instance)
            instance._tunableSettings[self.name] = setting
        return setting

    def __get__(self, instance:TUNABLE_SELF_T, owner:Any=None) -> TunableSetting[TUNABLE_T,TUNABLE_SELF_T]:
        #setting = getattr(instance, self.settingName, None)
        #if setting is None: return self.default
        setting = self.__getSetting( instance )
        return setting

    def __set__(self, instance:TUNABLE_SELF_T, value:TUNABLE_T) -> None:
        assert instance is not None,  f"Cannot set {self.name} "
        setting =  self.__getSetting( instance )
        setting.settingUpdate(value)

TunableDescriptorT = GenericT(TunableDescriptor)

TUNABLE_DESCRIPTOR_T=TypeVar('TUNABLE_DESCRIPTOR_T' ) #, bound='TunableDescriptor')
#############################################################################

class Tunable(NliInterface):
    
    def __init__(self) -> None:
        self._tunableSettings:Dict[str,TunableSetting[Any,Self]] = {}
        
    def onSettingUpdate( self, setting:TunableSetting[TUNABLE_T,Self]) -> None:
        pass
        

#############################################################################

def tunableProperty(  default:TUNABLE_T, 
            descriptorClass:Type[TUNABLE_DESCRIPTOR_T],
            **kwds:Unpack[TUNABLE_SETTING_KWDS[TUNABLE_T,TUNABLE_SELF_T]]
    ) -> Callable[ 
            [Callable[[TUNABLE_SELF_T,TunableSetting[TUNABLE_T,TUNABLE_SELF_T],EvaluationContext],
                         None]],
                  TUNABLE_DESCRIPTOR_T]:
    def decorated( onChange:Callable[
                        [TUNABLE_SELF_T,TunableSetting[TUNABLE_T, TUNABLE_SELF_T], EvaluationContext], None] 
                        ) -> TUNABLE_DESCRIPTOR_T:
        kwds.setdefault('startingValue', default)
        kwds.setdefault('name', onChange.__name__)
        kwds.setdefault('onChange', onChange) # type: ignore
        descriptor:TUNABLE_DESCRIPTOR_T = descriptorClass(  
                **kwds  # type: ignore
            ) 
        return descriptor # type: ignore
    return decorated


tunablePropertyT = GenericT(tunableProperty)
#############################################################################

__profileImport.complete(globals())
    
__all__ = [
            'Tunable', 'TunableSetting', 'TunableSettingT',
            'TunableDescriptor','TunableDescriptorT',
            'TUNABLE_SELF_T',
            'tunableProperty', 'tunablePropertyT'
         
           ]
