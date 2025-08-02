from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayAudioEffectImport = getImportProfiler( globals() ) # "Audio.Effect"

import ulab.numpy as np
import synthio, array, math

from LumensalisCP.IOContext import *
from LumensalisCP.Main.Dependents import MainChild
from LumensalisCP.Identity.Local import NamedLocalIdentifiable
from LumensalisCP.util.LiveProperty  import *
from random import random

if TYPE_CHECKING:
    from .Audio import Audio
    WaveDataType:TypeAlias = Union[bytes, bytearray, array.array[int], memoryview, np.ndarray]
    WaveArgType:TypeAlias = Union[str, WaveDataType]

#############################################################################

_sayAudioEffectImport.parsing()

class SoundEffectsManager(MainChild):
    theEffectManager: 'SoundEffectsManager'

    def __init__(self, audio: Audio, **kwds: Unpack[MainChild.KWDS]) -> None:
        kwds.setdefault("main", audio.main)
        super().__init__(**kwds)

        self.audio = audio

        #sample_rate=22050

        self.synth = synthio.Synthesizer( sample_rate=44100 )
        audio.audio.play(self.synth) # type: ignore

        self.waveForms:dict[str,WaveDataType] = {
            #'sine': synthio.Waveform.SINE,
            #'square': synthio.Waveform.SQUARE,
            #'triangle': synthio.Waveform.TRIANGLE,
            #'sawtooth': synthio.Waveform.SAWTOOTH,
        }   

        waveformSize = 8192  #  sample_rate
        sine_wave = array.array("h", [0] * waveformSize)
        for i in range(waveformSize):
            sine_wave[i] = int(32767 * math.sin(2 * math.pi * i / waveformSize) )
        

        self.waveForms['sine_wave'] = sine_wave
        wMin = -32767
        wMax = 32767
        self.waveForms['saw']  = array.array("h", [wMin, 0, wMax ] )
        self.waveForms['square']  = array.array("h", ([wMin]*10) + ([wMax]*10) ) 
        self.waveForms['noise']  = array.array("h", [int((random() -0.5) * 65000) for  _ in range(1024)] )

        if self.enableDbgOut: self.dbgOut(f"Created sine_wave with size {waveformSize} : {repr(sine_wave):.80}...")

    def _makeEffect(self, effectClass:Optional[type]=None, **kwargs:Any) -> SoundEffect:
        effectClass = effectClass or SoundEffect
        effect = effectClass(self, **kwargs)
        effect.postCreate()
        return effect
    
    def makeEffect(self, **kwargs:Unpack[SoundEffect.KWDS]) -> SoundEffect:
        return self._makeEffect(SoundEffect, **kwargs)

    def getWave(self, wave: WaveArgType) -> WaveDataType:
        if isinstance(wave, str):
            return self.waveForms[wave]
        return wave

#############################################################################

SioBlockInput:TypeAlias = Union[synthio.LFO,synthio.Math,float]
EvalSioBlockInput:TypeAlias = Union[EvaluatableT[float], SioBlockInput]


# pyright: reportPrivateUsage=false
#if TYPE_CHECKING:
from LumensalisCP.util.LiveProperty import _LCT, _LPT

#############################################################################

class LiveBlockInputPropertyWrapper(Generic[_LCT,_LPT], Debuggable):
    """ wrapper for use with LiveWrappedPropertyDescriptor

    redirects 'name' to property on 'member' instance, with Evaluatable handling

    """

    _inputChangedSubscriptions: list[tuple[InputSource,Callable[...,None]]]
                                     
    def __init__(self, instance:_LCT,  name:str,
            default:EvalSioBlockInput|None = None, owner:Any = None, member:str|None=None ) -> None:
        Debuggable.__init__(self)
        assert member is not None, "member must be specified"
        self.member = member
        self.isEvaluatable = isinstance(default, Evaluatable)
        if self.isEvaluatable:
            self._evalName:str = f"_eval_{name}"
        self.value = default

    def get(self,name:str, instance:_LCT)-> EvalSioBlockInput:
        if self.isEvaluatable:
            return getattr( instance, self._evalName)
        return getattr( getattr(instance,self.member), name)

    def _unsubscribe( self,  instance:_LCT ) -> None:
        if len(self._inputChangedSubscriptions) > 0:
            for input, cb in self._inputChangedSubscriptions:
                input.removeOnChange(cb)
            self._inputChangedSubscriptions.clear()

    def _subscribe( self, name:str, value:EvalSioBlockInput, instance:_LCT ) -> None:
        assert isinstance(value, Evaluatable), f"Expected Evaluatable, got {type(value)}"
        if self.enableDbgOut:
            self.dbgOut(f"Subscribing to changes to {self.member}.{name} in {instance}")
        self._unsubscribe(instance)
        def changedCallback(source:InputSource, context:EvaluationContext) -> None:
            eValue =  getattr( instance, self._evalName) 
            assert isinstance(eValue, Evaluatable), f"Expected Evaluatable, got {type(eValue)}"
            value = context.valueOf(eValue)
            if self.enableDbgOut: self.dbgOut(f"Input source {source.name} changed, updating {self.member}.{name} to {value}")
            setattr(getattr(instance, self.member), name, value)

        for dependency in value.dependencies():
            if isinstance(dependency, InputSource):
                dependency.onChange(changedCallback)
                self._inputChangedSubscriptions.append((dependency, changedCallback))
        if self.enableDbgOut:
            self.dbgOut(
                 f"  {len(self._inputChangedSubscriptions)} inputChanged subscriptions for {name} in {instance}"
                               )
            
    def set(self,name:str, instance:_LCT, value:EvalSioBlockInput) -> None:
        if self.enableDbgOut:
            self.dbgOut(f"set {name}={value} in {instance}")

        if isinstance(value, Evaluatable):
            if not self.isEvaluatable:
                self.isEvaluatable = True
                if not hasattr(self,'_evalName'): 
                    setattr(self, '_evalName', f"_eval_{name}")
                    self._inputChangedSubscriptions = []
            else:
                self._unsubscribe(instance)
            self._subscribe(name, value, instance)
            setattr( instance, self._evalName, value )
            value = value.getValue(UpdateContext.fetchCurrentContext(None))
        else:
            if self.isEvaluatable:
                self._unsubscribe(instance)
                self.isEvaluatable = False
            self.isEvaluatable = False

        setattr( getattr( instance, self.member), name, value )


if TYPE_CHECKING:
        
    class LivePropertyEvSFXBlockInput( LiveWrappedPropertyDescriptor['SoundEffect',EvalSioBlockInput] ): pass
    class LivePropertyEvLFOBlockInput( LiveWrappedPropertyDescriptor['EffectLFO',EvalSioBlockInput] ): pass

    class WrappedBlockInputProperty( LiveWrappedPropertyDescriptor[_LCT, EvalSioBlockInput] ):
        def __init__(self,  member:str, *args:Any, **kwds:Any ) -> None: ...
            #super().__init__(
            #    LiveBlockInputPropertyWrapper[_LCT,EvalSioBlockInput],
            #      *args, **kwds)
else:
    class WrappedBlockInputProperty( LiveWrappedPropertyDescriptor ):
        def __init__(self, member:str, *args, **kwds ):
            kwds['member'] = member
            super().__init__(LiveBlockInputPropertyWrapper, *args, **kwds)

    LivePropertyEvSFXBlockInput = WrappedBlockInputProperty
    LivePropertyEvLFOBlockInput = WrappedBlockInputProperty

#############################################################################


class EffectNoteProperty(LivePropertyEvSFXBlockInput):

    def _reportSet(self, instance:SoundEffect, value:EvalSioBlockInput) -> None:
        if instance.enableDbgOut:
            instance.dbgOut(f"Note property {self.name} set to {value}")

        instance.onNoteAttrSet(self.name, value)

#############################################################################

class EffectFilterProperty(LivePropertyEvSFXBlockInput):

    def _reportSet(self, instance:SoundEffect, value:EvalSioBlockInput) -> None:
        instance.onFilterAttrSet(self.name, value)

#############################################################################

LOW_PASS = synthio.FilterMode.LOW_PASS
HIGH_PASS = synthio.FilterMode.HIGH_PASS
BAND_PASS = synthio.FilterMode.BAND_PASS
NOTCH = synthio.FilterMode.NOTCH
# filters beyond this line use the "A" parameter (in addition to f0 and Q)
PEAKING_EQ = synthio.FilterMode.PEAKING_EQ # type: ignore
LOW_SHELF = synthio.FilterMode.LOW_SHELF # type: ignore
HIGH_SHELF = synthio.FilterMode.HIGH_SHELF # type: ignore

_filterModes:dict[str,Any] = dict( LOW_PASS=LOW_PASS,
                     HIGH_PASS=HIGH_PASS,
                     BAND_PASS=BAND_PASS,   
                     NOTCH=NOTCH,
                     PEAKING_EQ=PEAKING_EQ, # type: ignore
                     LOW_SHELF=LOW_SHELF, # type: ignore
                     HIGH_SHELF=HIGH_SHELF # type: ignore
                     )

class EffectLFO(NamedLocalIdentifiable):

    def __init__(self, **kwds: Unpack[NamedLocalIdentifiable.KWDS]) -> None:
        self.lfo = synthio.LFO()

    rate:WrappedBlockInputProperty[Self] =  WrappedBlockInputProperty( 'lfo','rate', 1.0 )
    offset:WrappedBlockInputProperty[Self] = WrappedBlockInputProperty( 'lfo', 'offset', 0.0 )
    phase_offset:WrappedBlockInputProperty[Self] = WrappedBlockInputProperty( 'lfo', 'phase_offset', 0.0 )
    scale:WrappedBlockInputProperty[Self] = WrappedBlockInputProperty( 'lfo', 'scale', 0.0 )
    
    def onDescriptorSet(self, name:str, value:Any) -> None:
        if self.enableDbgOut:
            self.dbgOut(f"EffectLFO property {name} set to {value}")
        if not isinstance(value, (int, float, synthio.LFO)):
            if isinstance(value, Evaluatable):
                context = UpdateContext.fetchCurrentContext(None)
                value = context.valueOf(value)
            else:
                raise TypeError(f"EffectLFO property {name} must be a number or LFO, not {type(value)}")

        setattr(self.lfo, name, value)

    
class SoundEffect(NamedLocalIdentifiable):

    class KWDS(NamedLocalIdentifiable.KWDS):
        frequency: NotRequired[float] 
        wave: NotRequired[WaveArgType]
        filter: NotRequired[synthio.Biquad]
        filterMode: NotRequired[synthio.FilterMode|str]
        filterFrequency: NotRequired[float]
        filterQ: NotRequired[float|Evaluatable[float]]
        filterA: NotRequired[float|Evaluatable[float]]
        

    def __init__(self, effectsManager: SoundEffectsManager, 
                frequency: Any = 440,  # Default frequency for the note
                wave: WaveArgType = 'sine_wave',
                filter: Optional[synthio.Biquad] = None,
                filterMode: Optional[synthio.FilterMode|str] = None,
                filterFrequency: Optional[float] = None,
                filterQ: Optional[float|Evaluatable[float]] = None,
                filterA: Optional[float|Evaluatable[float]] = None, 
                 **kwargs: Unpack[NamedLocalIdentifiable.KWDS]
                ) -> None:
        NamedLocalIdentifiable.__init__(self, **kwargs)

        waveform=effectsManager.getWave(wave)
        if self.enableDbgOut: self.dbgOut(f"Creating Effect with frequency {frequency} and waveform {repr(waveform):.80}...")
        if isinstance(filterMode,str):
            filterMode = _filterModes.get(filterMode)
            assert filterMode is not None, f"Unknown filter mode {filterMode}"
        if filter is not None:
            assert filterFrequency is None, "Cannot specify both filter and filterFrequency"
            assert filterQ is None, "Cannot specify both filter and filterQ"
            assert filterA is None, "Cannot specify both filter and filterA"
            assert filterMode is None, "Cannot specify both filter and filterMode"
        elif filterMode is not None:
            if filterFrequency is None:
                filterFrequency = 1000.0
            if filterQ is None:
                filterQ = 0.707
            if filterA is None:
                filterA = 0.0

            filter = synthio.Biquad(
                 mode=filterMode,  # type: ignore
                frequency=filterFrequency,  # type: ignore
                Q=filterQ,  # type: ignore
                A=filterA  # type: ignore
            )

        self.note = synthio.Note(
            frequency=frequency,
            waveform=waveform,
            filter=filter,
        )
        self._playing = False
        self.effectsManager = effectsManager
        if filter is not None:
            self.filter: synthio.Biquad = filter
            self.infoOut( "filter set to %r", filter )

    amplitude:WrappedBlockInputProperty[Self] = WrappedBlockInputProperty('note','amplitude', 1.0 )
    bend:WrappedBlockInputProperty[Self] = WrappedBlockInputProperty('note','bend', 0.0 )

    filterFrequency:WrappedBlockInputProperty[Self] = WrappedBlockInputProperty('filter','frequency', 0.0 )

    def onNoteAttrSet(self, name:str, value:EvalSioBlockInput) -> None:
        """Called when a note property is set"""
        if self.enableDbgOut: self.dbgOut(f"Note property {name} set to {value}")
        setattr(self.note, name, value)

    def onFilterAttrSet(self, name:str, value:EvalSioBlockInput) -> None:
        if self.enableDbgOut: self.dbgOut(f"Filter property {name} set to {value}")
        setattr(self.filter, name, value)
        
    @property
    def playing(self) -> bool:
        return self._playing
    
    def toggle(self, context:Optional[EvaluationContext]=None) -> None:
        if self._playing:
            self.stop()
        else:
            self.start()

    def start(self, context:Optional[EvaluationContext]=None) -> None:
        if self._playing:
            if self.enableDbgOut: self.dbgOut("start() ... already started")
            return
        self._playing = True
        self.effectsManager.synth.press(self.note)
        if self.enableDbgOut: self.dbgOut("Effect started")

    def stop(self, context:Optional[EvaluationContext]=None) -> None:
        if not self._playing:
            if self.enableDbgOut: self.dbgOut("stop() ... not playing")
            return
        self._playing = False
        self.effectsManager.synth.release(self.note)
        if self.enableDbgOut: self.dbgOut("Effect stopped")

    def postCreate(self) -> None:
        """ called after the effect is created, to allow for additional setup """
        if self.enableDbgOut: self.dbgOut("Effect postCreate called")
        pass

_sayAudioEffectImport.complete(globals())

__all__ = [
    "SoundEffectsManager",
    "SoundEffect",
    "EffectLFO",
    #"WaveDataType",
    #"WaveArgType",
    "LOW_PASS",
    "HIGH_PASS",
    "BAND_PASS",
    "NOTCH",
    "PEAKING_EQ",
    "LOW_SHELF",
    "HIGH_SHELF",
]
