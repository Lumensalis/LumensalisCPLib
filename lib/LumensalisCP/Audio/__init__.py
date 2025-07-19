

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *

import audiomp3, audiobusio, board, audiocore, math, audiomixer
from microcontroller import Pin
import array
import LumensalisCP.Main.Manager
from  LumensalisCP.Main.Dependents import MainChild

# TODO : recheck / fix everything with # type: ignore

if TYPE_CHECKING:
    from  LumensalisCP.Main.Manager import MainManager
    
class AudioSample( object ):
    def __init__( self, sample, filename ):
        self.sample = sample
        self.filename = filename
    
    def play(self, loop:bool = False, **kwds):
        #Audio.theAudio.mixer.play(self.sample)
        Audio.theAudio.play(self, loop=loop, **kwds)
        
        
class Audio( MainChild ):
    theAudio:'Audio'

    def __init__( self, 
                main:MainManager,
                bit_clock:Pin|None = None, 
                word_select:Pin|None= None, 
                data:Pin|None= None, 
                useMixer:bool=False,
                mixer_sample_rate = 22050,
                mixer_channel_count=1,
                mixer_signed = False,
                mixer_bits_per_sample = 16,
                mixer_voice_count = 2,
                mixer_buffer_size = 2048,
            ):
        super().__init__(main=main,name="Audio")
        assert getattr(Audio,'theAudio',None) is None
        Audio.theAudio = self
        
        bit_clock = bit_clock or board.IO14
        word_select = word_select or board.IO13
        data = data or board.IO15 
        self.audio = audiobusio.I2SOut( bit_clock=bit_clock, word_select=word_select, data=data )
        
        self.mixer: audiomixer.Mixer|None = None
        if useMixer:
            self.__mixerConfig = dict(
                voice_count = mixer_voice_count,
                sample_rate = mixer_sample_rate,
                channel_count=mixer_channel_count,
                samples_signed = bool(mixer_signed),
                bits_per_sample = mixer_bits_per_sample,
                buffer_size = mixer_buffer_size, 
            )
            self.mixer = audiomixer.Mixer( **self.__mixerConfig ) # type: ignore
            self.audio.play( self.mixer )
            
        self.__masterVolume = 1.0
        self.__sampleVolume = 1.0
        
        
    @property 
    def volume(self): return self.__masterVolume
    
    @volume.setter
    def volume(self, level:float ):
        self.__masterVolume = max(0.0, min(1.0,float(level)))
        if self.mixer is not None:
            self.mixer.voice[0].level = self.__masterVolume * self.__sampleVolume
        
    def play( self, sample:AudioSample, loop:bool=False, level:float = 1.0, voice:int = 0 ):
        if self.enableDbgOut: self.dbgOut( "playing %s, loop=%s", sample.filename, loop )
        self.__sampleVolume = max(0.0, min(1.0,float(level)))
        if self.mixer is not None:
            self.mixer.voice[voice].level =  self.__masterVolume * self.__sampleVolume
            self.mixer.play(sample.sample, loop=loop)
        else:
            self.audio.play(sample.sample, loop=loop)
        
        
    def readSample( self, filename:str ):
        sample = None
        if filename.endswith(".mp3"):
            sample = audiomp3.MP3Decoder(filename) # type: ignore


        if filename.endswith(".wav"):
            wave_file = open(filename, "rb")
            sample = audiocore.WaveFile(wave_file) # type: ignore

        assert sample is not None
        if self.enableDbgOut: self.dbgOut( f"sample {filename} at {sample.sample_rate} is {sample}" )
        if self.mixer is not None:
            for tag in [ 'sample_rate', 'bits_per_sample', 'channel_count' ]:
                vSample, vMixer  =  getattr(sample,tag),  self.__mixerConfig[tag]
                ensure( vSample == vMixer,
                    "sample %r : %s is %s, mixer requires %s",
                    filename, tag, vSample, vMixer )

        return  AudioSample( sample, filename=filename )

    def readSamples( self, *filenames:str ) -> List[AudioSample]:
        rv = []
        for filename in filenames:
            rv.append( self.readSample( filename ) )
        return rv
        
    def stop(self, voice:int = 0):
        if self.enableDbgOut: self.dbgOut( "stopping" )
        if self.mixer is not None:
            self.mixer.stop_voice(voice=voice)
        else:
            self.audio.stop()
        
    def makeSine(self):
        
        sample_rate = 8000
        tone_volume = .1  # Increase or decrease this to adjust the volume of the tone.
        frequency = 440  # Set this to the Hz of the tone you want to generate.
        length = sample_rate // frequency  # One frequency period
        sine_wave = array.array("H", [0] * length)
        for i in range(length):
            sine_wave[i] = int((math.sin(math.pi * 2 * frequency * i / sample_rate) *
                                tone_volume + 1) * (2 ** 15 - 1))
        sine_wave_sample = audiocore.RawSample(sine_wave, sample_rate=sample_rate)
        return sine_wave_sample
