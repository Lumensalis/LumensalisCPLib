from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__profileImport = getImportProfiler( globals() ) # "Outputs"

# pyright: reportUnusedImport=false

from LumensalisCP.Eval.Expressions import *
from LumensalisCP.Outputs import NamedNotifyingOutputTarget, NotifyingOutputTargetT,OutputTarget
from LumensalisCP.Interactable import Interactable, InteractableT, INTERACTABLE_ARG_T, INTERACTABLE_T, INTERACTABLE_ARG_T_KWDST

#############################################################################

__profileImport.parsing()


#############################################################################
TUNABLE_ARG_T=TypeVar('TUNABLE_ARG_T')
TUNABLE_T=TypeVar('TUNABLE_T')
TUNABLE_SELF_T=TypeVar('TUNABLE_SELF_T', bound='Tunable')


#############################################################################

class TUNABLE_SETTING_KWDS(INTERACTABLE_ARG_T_KWDST[TUNABLE_ARG_T, TUNABLE_T], 
                           NamedNotifyingOutputTarget.KWDS,
                           Generic[TUNABLE_ARG_T, TUNABLE_T,TUNABLE_SELF_T]
                    ):
    onChange: NotRequired[
         Callable[[TUNABLE_SELF_T, TunableSetting[TUNABLE_ARG_T, TUNABLE_T,TUNABLE_SELF_T], EvaluationContext], None] ]

TUNABLE_SETTING_KWDS_T = GenericT(TUNABLE_SETTING_KWDS)

#############################################################################

class TunableSetting(NamedLocalIdentifiable,OutputTarget,
                     InteractableT[TUNABLE_ARG_T,TUNABLE_T],
                     EvaluatableT[TUNABLE_T],
                     Generic[TUNABLE_ARG_T, TUNABLE_T,TUNABLE_SELF_T]):


    def __init__(self, tunable:TUNABLE_SELF_T, **kwargs:Unpack[TUNABLE_SETTING_KWDS[TUNABLE_ARG_T,TUNABLE_T,TUNABLE_SELF_T]]) -> None:
        self.onChange = kwargs.pop('onChange', None)
        value = kwargs.get('startingValue', None)
        assert value is not None, "TunableSetting must have a startingValue"

        self.__tunable = weakref.ref(tunable)
        nliArgs = NamedLocalIdentifiable.extractInitArgs(kwargs)
        NamedLocalIdentifiable.__init__(self, **nliArgs)
        InteractableT[TUNABLE_ARG_T,TUNABLE_T].__init__(self, **kwargs)
        
        self.__value:TUNABLE_T = value # type: ignore

    def set( self, value:Any, context:EvaluationContext ) -> None:
        # from OutputTarget
        self.settingUpdate(value, context)
        

    def settingUpdate( self, value:TUNABLE_ARG_T, context:Optional[EvaluationContext]=None ) -> None:
        v = self.interactConvert(value)
        if v == self.__value:
            if self.enableDbgOut: self.dbgOut("settingUpdate no change: %s", v)
            return
        self.__value = v
        if self.enableDbgOut: self.dbgOut("settingUpdate changed: %s", v)

        if context is None:
            context = UpdateContext.fetchCurrentContext(context)

        if self.onChange:
            self.onChange(self.__tunable(), self, context)



    @property
    def value(self) -> TUNABLE_T:
        return self.__value
    
    def __call__(self, context:Optional[EvaluationContext]=None) -> TUNABLE_T:
        return self.__value
    
TunableSettingT = GenericT(TunableSetting)


#############################################################################
class TunableDescriptor(Generic[TUNABLE_ARG_T,TUNABLE_T,TUNABLE_SELF_T]):
    def __init__(self, settingClass:type, 
                 **settingKwds:Unpack[TUNABLE_SETTING_KWDS[TUNABLE_ARG_T,TUNABLE_T,TUNABLE_SELF_T]] # type: ignore
                 ) -> None:
        name = settingKwds.get('name', None)
        default = settingKwds.get('startingValue', None)
        assert name is not None and default is not None, "TunableDescriptor must have a name and default value"
        self.name = name
        self.settingClass = settingClass
        self.settingName = f"_ts_{name}"
        self.default:TUNABLE_T = default # type: ignore
        self._settingKwds = settingKwds 

    def __makeSetting(self, instance:TUNABLE_SELF_T) -> TunableSetting[TUNABLE_ARG_T,TUNABLE_T,TUNABLE_SELF_T]:
        assert getattr(instance, self.settingName, None) is None
        settings:TUNABLE_SETTING_KWDS[TUNABLE_ARG_T,TUNABLE_T,TUNABLE_SELF_T] = dict(self._settingKwds)
        #settings['name'] = self.name
        #settings.setdefault('startingValue', self.default)
        setting:TunableSetting[TUNABLE_ARG_T,TUNABLE_T,TUNABLE_SELF_T] = \
                                self.settingClass( instance, **settings )
        setattr(instance, self.settingName, setting)
        return setting

    def __getSetting(self, instance:TUNABLE_SELF_T) -> TunableSetting[TUNABLE_ARG_T,TUNABLE_T,TUNABLE_SELF_T]:
        setting = getattr(instance, self.settingName, None)
        if setting is None:
            setting = self.__makeSetting(instance)
            instance._tunableSettings[self.name] = setting
        return setting

    def __get__(self, instance:TUNABLE_SELF_T, owner:Any=None) -> TunableSetting[TUNABLE_ARG_T,TUNABLE_T,TUNABLE_SELF_T]:
        #setting = getattr(instance, self.settingName, None)
        #if setting is None: return self.default
        setting = self.__getSetting( instance )
        return setting

    def __set__(self, instance:TUNABLE_SELF_T, value:TUNABLE_ARG_T) -> None:
        assert instance is not None,  f"Cannot set {self.name} "
        setting =  self.__getSetting( instance )
        setting.settingUpdate(value)

TunableDescriptorT = GenericT(TunableDescriptor)
#############################################################################

class Tunable(NliInterface):
    
    def __init__(self) -> None:
        self._tunableSettings:Dict[str,TunableSetting[Any,Any,Self]] = {}
        
    def onSettingUpdate( self, setting:TunableSetting[TUNABLE_ARG_T,TUNABLE_T,Self]) -> None:
        pass
        

#############################################################################

class TunableBoolSetting_KWDS(TUNABLE_SETTING_KWDS_T[bool,bool,TUNABLE_SELF_T]):
    pass

class TunableBoolSetting(TunableSettingT[bool,bool,TUNABLE_SELF_T]):

    def __init__(self, tunable: TUNABLE_SELF_T, **kwargs:Unpack[TunableBoolSetting_KWDS[TUNABLE_SELF_T]]) -> None:
        kwargs.setdefault('kind', bool)
        kwargs.setdefault('kindMatch', bool)
        super().__init__( tunable, **kwargs)

TunableBoolSettingT = GenericT(TunableBoolSetting)

#############################################################################

class TunableFloatSetting_KWDS(TUNABLE_SETTING_KWDS_T[Union[int,float],float,TUNABLE_SELF_T]):
    pass

class TunableFloatSetting(TunableSettingT[Union[int,float],float,TUNABLE_SELF_T]):

    def __init__(self, tunable: TUNABLE_SELF_T, **kwargs:Unpack[TunableFloatSetting_KWDS[TUNABLE_SELF_T]]) -> None:
        kwargs.setdefault('kind', float)
        kwargs.setdefault('kindMatch', float)
        super().__init__( tunable, **kwargs)

TunableFloatSettingT = GenericT(TunableFloatSetting)

#############################################################################

class TunableIntSetting_KWDS(TUNABLE_SETTING_KWDS_T[int,int,TUNABLE_SELF_T]):
    pass

class TunableIntSetting(TunableSettingT[int,int,TUNABLE_SELF_T]):

    def __init__(self, tunable: TUNABLE_SELF_T, **kwargs:Unpack[TunableIntSetting_KWDS[TUNABLE_SELF_T]]) -> None:
        kwargs.setdefault('kind', int)
        kwargs.setdefault('kindMatch', int)
        super().__init__( tunable, **kwargs)

#############################################################################
class TunableZeroToOneSetting_KWDS(TUNABLE_SETTING_KWDS_T[ZeroToOne,ZeroToOne,TUNABLE_SELF_T]):
    pass

class TunableZeroToOneSetting(TunableSettingT[ZeroToOne,ZeroToOne,TUNABLE_SELF_T]):
    def __init__(self, tunable: TUNABLE_SELF_T, **kwargs:Unpack[TunableZeroToOneSetting_KWDS[TUNABLE_SELF_T]]) -> None:
        kwargs.setdefault('kind', ZeroToOne)
        kwargs.setdefault('kindMatch', ZeroToOne)
        kwargs.setdefault('min', ZeroToOne(0.0))
        kwargs.setdefault('max', ZeroToOne(1.0))
        super().__init__( tunable, **kwargs)

TunableZeroToOneSettingT = GenericT(TunableZeroToOneSetting)

class TunableZeroToOneDescriptor(TunableDescriptorT[ZeroToOne,ZeroToOne,TUNABLE_SELF_T]):
    pass

TunableZeroToOneDescriptorT = GenericT(TunableZeroToOneDescriptor)

def tunableZeroToOne(  default:ZeroToOne, **kwds:Unpack[TunableZeroToOneSetting.KWDS]
                ) -> Callable[ 
                        [Callable[[TUNABLE_SELF_T,TunableZeroToOneSetting[TUNABLE_SELF_T],EvaluationContext], None]],
                  TunableZeroToOneDescriptor[TUNABLE_SELF_T]]:
    def decorated( onChange:Callable[
                        [TUNABLE_SELF_T,TunableZeroToOneSetting[TUNABLE_SELF_T], EvaluationContext],
             None] ) -> TunableZeroToOneDescriptor[TUNABLE_SELF_T]:
        kwds.setdefault('name', onChange.__name__)
        kwds.setdefault('startingValue', default)
        #kwds.setdefault('onChange', onChange)
        descriptor:TunableZeroToOneDescriptor[TUNABLE_SELF_T] = TunableZeroToOneDescriptorT[TUNABLE_SELF_T](  TunableZeroToOneSettingT[TUNABLE_SELF_T], **kwds )
        return descriptor
    return decorated

#############################################################################

class TunablePlusMinusOneSetting_KWDS(TUNABLE_SETTING_KWDS_T[PlusMinusOne,PlusMinusOne,TUNABLE_SELF_T]):
    pass

class TunablePlusMinusOneSetting(TunableSettingT[PlusMinusOne,PlusMinusOne,TUNABLE_SELF_T]):
    def __init__(self, tunable: TUNABLE_SELF_T, **kwargs:Unpack[TunablePlusMinusOneSetting_KWDS[TUNABLE_SELF_T]]) -> None:
        kwargs.setdefault('kind', PlusMinusOne)
        kwargs.setdefault('kindMatch', PlusMinusOne)
        kwargs.setdefault('min', PlusMinusOne(-1))
        kwargs.setdefault('max', PlusMinusOne(1))
        super().__init__( tunable, **kwargs)

TunablePlusMinusOneSettingT = GenericT(TunablePlusMinusOneSetting)

class TunablePlusMinusOneDescriptor(TunableDescriptorT[PlusMinusOne,PlusMinusOne,TUNABLE_SELF_T]):
    pass

TunablePlusMinusOneDescriptorT = GenericT(TunablePlusMinusOneDescriptor)

def tunablePlusMinusOne(  default:PlusMinusOne,
                         **kwds:Unpack[TunablePlusMinusOneSetting_KWDS[TUNABLE_SELF_T]]
        ) -> Callable[ [Callable[[TUNABLE_SELF_T,TunablePlusMinusOneSetting[TUNABLE_SELF_T],EvaluationContext], None]],  TunablePlusMinusOneDescriptor[TUNABLE_SELF_T]]:
    def decorated( onChange:Callable[[TUNABLE_SELF_T,TunablePlusMinusOneSetting[TUNABLE_SELF_T],EvaluationContext], None] 
                  ) -> TunablePlusMinusOneDescriptor[TUNABLE_SELF_T]:
        kwds.setdefault('startingValue', default)
        kwds.setdefault('name', onChange.__name__)
        kwds.setdefault('onChange', onChange)
        descriptor:TunablePlusMinusOneDescriptor[TUNABLE_SELF_T] = TunablePlusMinusOneDescriptorT[TUNABLE_SELF_T](
             TunablePlusMinusOneSettingT[TUNABLE_SELF_T], **kwds )
        return descriptor
    return decorated

tunablePlusMinusOneT = GenericT(tunablePlusMinusOne)
#############################################################################

__profileImport.complete(globals())
    
__all__ = [
            'Tunable', 'TunableSetting', 'TunableSettingT',
            'TunableDescriptor','TunableDescriptorT',
            'TunableFloatSetting', 'TunableFloatSettingT',
            'TunableBoolSetting', 'TunableBoolSettingT',
            'tunableZeroToOne', 'TunableZeroToOneDescriptor', 'TunableZeroToOneSetting',
            'tunablePlusMinusOne', 'tunablePlusMinusOneT', 'TunablePlusMinusOneDescriptor', 'TunablePlusMinusOneSetting',
           ]
