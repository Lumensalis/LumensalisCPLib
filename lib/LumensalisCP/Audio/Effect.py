from __future__ import annotations

from LumensalisCP.Main.PreMainConfig import ImportProfiler
_sayAudioEffectImport = ImportProfiler( "Audio.Effect" )


import ulab.numpy as np
import synthio, array, math


from LumensalisCP.IOContext import *
from  LumensalisCP.Main.Dependents import MainChild
from  LumensalisCP.Identity.Local import NamedLocalIdentifiable

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

        #self.sample_rate=
        sample_rate=22050


        self.synth = synthio.Synthesizer( sample_rate=44100 )
        audio.audio.play(self.synth)

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
        if self.enableDbgOut: self.dbgOut(f"Created sine_wave with size {waveformSize} : {repr(sine_wave):.80}...")

    def _makeEffect(self, effectClass:Optional[type]=None, **kwargs:StrAnyDict) -> SoundEffect:
        effectClass = effectClass or SoundEffect
        effect = effectClass(self, **kwargs)
        effect.postCreate()
        return effect
    
    def makeEffect(self, **kwargs:SoundEffect.KWDS) -> SoundEffect:
        return self._makeEffect(SoundEffect, **kwargs)

    def getWave(self, wave: WaveArgType) -> WaveDataType:
        if isinstance(wave, str):
            return self.waveForms[wave]
        return wave

#############################################################################
LOW_PASS = synthio.FilterMode.LOW_PASS
HIGH_PASS = synthio.FilterMode.HIGH_PASS
BAND_PASS = synthio.FilterMode.BAND_PASS
NOTCH = synthio.FilterMode.NOTCH
# filters beyond this line use the "A" parameter (in addition to f0 and Q)
PEAKING_EQ = synthio.FilterMode.PEAKING_EQ
LOW_SHELF = synthio.FilterMode.LOW_SHELF
HIGH_SHELF = synthio.FilterMode.HIGH_SHELF

class SoundEffect(NamedLocalIdentifiable):

    class KWDS(NamedLocalIdentifiable.KWDS):
        frequency: NotRequired[float] 
        wave: NotRequired[WaveArgType]
        filter: NotRequired[synthio.Biquad]
        filterMode: NotRequired[synthio.FilterMode]
        filterFrequency: NotRequired[float]
        filterQ: NotRequired[float|Evaluatable[float]]
        filterA: NotRequired[float|Evaluatable[float]]
        

    def __init__(self, effectsManager: SoundEffectsManager, 
                frequency: Any = 440,  # Default frequency for the note
                wave: WaveArgType = 'sine_wave',
                filter: Optional[synthio.Biquad] = None,
                filterMode: Optional[synthio.FilterMode] = None,
                filterFrequency: Optional[float] = None,
                filterQ: Optional[float|Evaluatable[float]] = None,
                filterA: Optional[float|Evaluatable[float]] = None, 
                 **kwargs: Unpack[NamedLocalIdentifiable.KWDS]
                ) -> None:
        NamedLocalIdentifiable.__init__(self, **kwargs)

        waveform=effectsManager.getWave(wave)
        if self.enableDbgOut: self.dbgOut(f"Creating Effect with frequency {frequency} and waveform {repr(waveform):.80}...")
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

            filter = synthio.Biquad( mode=filterMode,
                frequency=filterFrequency,
                Q=filterQ,
                A=filterA
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

    @property
    def playing(self) -> bool:
        return self._playing
    
    def start(self) -> None:
        if self._playing:
            if self.enableDbgOut: self.dbgOut("start() ... already started")
            return
        self._playing = True
        self.effectsManager.synth.press(self.note)
        if self.enableDbgOut: self.dbgOut("Effect started")

    def stop(self) -> None:
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

_sayAudioEffectImport.complete()

__all__ = [
    "SoundEffectsManager",
    "SoundEffect",
    "WaveDataType",
    "WaveArgType",
    "LOW_PASS",
    "HIGH_PASS",
    "BAND_PASS",
    "NOTCH",
    "PEAKING_EQ",
    "LOW_SHELF",
    "HIGH_SHELF",
]
