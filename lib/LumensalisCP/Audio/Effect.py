from __future__ import annotations

import ulab.numpy as np
import synthio, array, math

from LumensalisCP.common import *
from  LumensalisCP.Main.Dependents import MainChild
from  LumensalisCP.Identity.Local import NamedLocalIdentifiable
if TYPE_CHECKING:
    from .Audio import Audio
    WaveDataType:TypeAlias = Union[bytes, bytearray, array.array[int], memoryview, np.ndarray]
    WaveArgType:TypeAlias = Union[str, WaveDataType]






class EffectManager(MainChild):
    theEffectManager: 'EffectManager'

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

    def makeEffect(self, effectClass:Optional[type]=None, **kwargs:StrAnyDict) -> Effect:
        effectClass = effectClass or Effect
        effect = effectClass(self, **kwargs)
        #self.callPostCreate(effect)
        return effect
    
    def getWave(self, wave: WaveArgType) -> WaveDataType:
        if isinstance(wave, str):
            return self.waveForms[wave]
        return wave

class Effect(NamedLocalIdentifiable):
    class KWDS(NamedLocalIdentifiable.KWDS):
        frequency: NotRequired[float] 
        wave: NotRequired[WaveArgType]

    def __init__(self, effectsManager: EffectManager, 
                frequency: Any = 440,  # Default frequency for the note
                wave: WaveArgType = 'sine_wave',
                 **kwargs: Unpack[NamedLocalIdentifiable.KWDS]
                ) -> None:
        NamedLocalIdentifiable.__init__(self, **kwargs)

        waveform=effectsManager.getWave(wave)
        if self.enableDbgOut: self.dbgOut(f"Creating Effect with frequency {frequency} and waveform {repr(waveform):.80}...")
        self.note = synthio.Note(
            frequency=frequency,
            waveform=waveform
        )
        self._playing = False
        self.effectsManager = effectsManager

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

