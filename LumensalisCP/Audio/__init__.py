

import audiomp3, audiobusio, board, audiocore, math, audiomixer
from microcontroller import Pin
import array

class AudioSample( object ):
    def __init__( self, sample ):
        self.sample = sample
    
    def play(self):
        #Audio.theAudio.mixer.play(self.sample)
        Audio.theAudio.audio.play(self.sample)
        
        
class Audio( object ):
    theAudio = None
    
    def __init__( self,   bit_clock:Pin|None, word_select:Pin|None, data:Pin|None ):
        assert Audio.theAudio is None
        Audio.theAudio = self
        
        bit_clock = bit_clock or board.IO14
        word_select = word_select or board.IO13
        data = data or board.IO15 
        self.audio = audiobusio.I2SOut( bit_clock=bit_clock, word_select=word_select, data=data )
        self.mixer = audiomixer.Mixer(sample_rate = 44100)
        #self.audio.play(self.mixer )
        
    def readSample( self, filename:str ):
        sample = None
        if filename.endswith(".mp3"):
            sample = audiomp3.MP3Decoder(filename)
        
        if filename.endswith(".wav"):
            wave_file = open(filename, "rb")
            sample = audiocore.WaveFile(wave_file)
        
        assert sample is not None
        print( f"sample {filename} at {sample.sample_rate} is {sample}" )
        return  AudioSample( sample )
        
    def makeSine(self):
        
        sample_rate = 8000
        tone_volume = .1  # Increase or decrease this to adjust the volume of the tone.
        frequency = 440  # Set this to the Hz of the tone you want to generate.
        length = sample_rate // frequency  # One freqency period
        sine_wave = array.array("H", [0] * length)
        for i in range(length):
            sine_wave[i] = int((math.sin(math.pi * 2 * frequency * i / sample_rate) *
                                tone_volume + 1) * (2 ** 15 - 1))
        sine_wave_sample = audiocore.RawSample(sine_wave, sample_rate=sample_rate)
        return sine_wave_sample
