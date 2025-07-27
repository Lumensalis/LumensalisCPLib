# ALWAYS START WITH "from LumensalisCP.Simple import *"
from LumensalisCP.Simple import * # http://lumensalis.com/ql/h2Start
import ulab.numpy as np
import synthio, array, math
import synthio

#############################################################################
sayAtStartup( "start project" )
main = ProjectManager() #  http://lumensalis.com/ql/h2Main

# setup three different scenes : http://lumensalis.com/ql/h2Scenes
sceneClosed, sceneOpen, sceneMoving = main.addScenes( 3 ) 

# setup Control Inputs : http://lumensalis.com/ql/h2Controller
rbCycle = main.panel.addSeconds( startingValue=3.1, min=0.1, max=10.0 )
rbs = main.panel.addFloat( startingValue=0.6, min=0.1, max=3.0 )
handSafetyRange = main.panel.addMillimeters(startingValue=300, min=10 )

#############################################################################
# HARDWARE : http://lumensalis.com/ql/h2Hardware
# setup the Caernarfon Castle : http://lumensalis.com/ql/h2Caernarfon
caernarfon = main.TerrainTronics.addCaernarfon( )

lidServo = caernarfon.initServo( 1, movePeriod=0.05 )
ir = caernarfon.addIrRemote(codenames="dvd_remote")     
neoPixA = caernarfon.addNeoPixels(pixelCount=45) 
neoPixB = caernarfon.addNeoPixels(servoPin=3,pixelCount=35)
# setup neoPixel modules : http://lumensalis.com/ql/h2NeoPixels
firstTwoOnPixA          = neoPixA.nextNLights(2)
leftStoneLights         = neoPixA.ring(3)
centerStoneLights       = neoPixA.ring(7)
rightStoneLights        = neoPixA.ring(3)
frontLidStrip           = neoPixA.stick(8)
sceneIndicatorLights    = neoPixB.stick(8)
angleGaugeLights        = neoPixB.ring(12)

# StemmaQT modules
timeOfFlightSensor = main.i2cFactory.addVL530lx(updateInterval=0.25)
vcnl4040 = main.adafruitFactory.addVCNL4040()

lightSensor = vcnl4040.light
proximitySensor = vcnl4040.proximity
vcnl4040.light_integration_time = 2
vcnl4040.proximity_integration_time = 2
main.panel.monitor( lightSensor )
main.panel.monitor( proximitySensor )


sayAtStartup( "setup touch inputs" )
# setup touch inputs : http://lumensalis.com/ql/h2Touch
capTouch = main.adafruitFactory.addMPR121()
leftStoneTouch, centerStoneTouch, rightStoneTouch= capTouch.addInputs( 1, 2, 4 )
leftRimTouch, centerRimTouch, rightRimTouch= capTouch.addInputs( 5, 6, 7 )
bottomTouch = capTouch.addInput( 8 )

magInputs = main.adafruitFactory.addAW9523()
lidClosedMag    = magInputs.addInput(1)
lidOpenMag      = magInputs.addInput(2)

#############################################################################
sayAtStartup( "setup synth" )

audio = main.addI2SAudio(
    word_select=board.IO14,     # MAX98357 lrc:green
    bit_clock=board.IO13,       # MAX98357 bclk:yellow
    data=board.IO10,            # MAX98357 din:orange
)

if 1:
    testEffect = audio.effects.makeEffect()
    testEffect.enableDbgOut = True

    def touchNote() -> None:
        if testEffect.playing:
            print( "releasing note" )
            testEffect.stop()
        else:
            print( "startNote" )
            testEffect.start()

    fireOnRising( leftRimTouch, do( touchNote ) )
else:
    sample_rate = 22050        
    #synth = synthio.Synthesizer(sample_rate=44100)
    synth = synthio.Synthesizer(sample_rate=44100)
    audio.audio.play(synth)

    waveformSize = 1024 #  sample_rate
    sine_wave = array.array("h", [0] * waveformSize)
    for i in range(waveformSize):
        sine_wave[i] = int(32767 * math.sin(2 * math.pi * i / waveformSize) )

    print(f"Created sine_wave with size {waveformSize} : {repr(sine_wave):.80}...")
    note = synthio.Note(frequency=440, waveform=sine_wave)
    note_state = dict( is_playing = False )


    def touchNote() -> None:
        if note_state['is_playing']:
            print( "releasing note" )
            synth.release(note)
        else:
            print( "startNote" )
            synth.press(note)  # Middle C
        note_state['is_playing'] = not note_state['is_playing']

    fireOnRising( leftRimTouch, do( touchNote ) )

main.panel.monitor( leftRimTouch )

    
#############################################################################
sayAtStartup( "setup lid" )
# setup lid  : http://lumensalis.com/ql/h2ServoDoor
lid = Motion.ServoDoor( lidServo, 
    closedPosition = 126,
    openPosition = 14,
    defaultSpeed= 12,
    openedSensor = lidOpenMag,
    closedSensor = lidClosedMag,
)

# change scene when lid reaches open/closed positions ...
lid.opened.setScene( sceneOpen )
lid.closed.setScene( sceneClosed )
lid.opening.setScene( sceneMoving )
lid.closing.setScene( sceneMoving )

#############################################################################
sayAtStartup( "setup actions" )
# setup actions http://lumensalis.com/ql/h2Actions
# and remote control : http://lumensalis.com/ql/h2IrRemote

handTooClose = timeOfFlightSensor.range < handSafetyRange

ir.onCode( "DOWN", do( lid.close ).unless( handTooClose ) )
ir.onCode( "UP", do( lid.open ) )
ir.onCode( "NEXT", do( main.scenes.switchToNextIn, ["sceneClosed","sceneOpening","sceneOpen","sceneClosing"] ) )

fireOnRising( rightStoneTouch, lid.open )
fireOnRising( rightRimTouch, lid.close )

#############################################################################
# http://lumensalis.com/ql/h2Oscillators
oscillator2 = Oscillator.Oscillator( low = 0.3, high = 2, frequency = 0.1 )
oscillator = Oscillator.Oscillator(  low = 0, high = 10, frequency = oscillator2 )

#############################################################################
# setup LED patterns : http://lumensalis.com/ql/h2Patterns
sayAtStartup( "setup patterns" )

frontLidBlink = PatternTemplate( Blink, frontLidStrip, onTime=0.25, offTime=0.25 )

frontLidStripPattern = Cylon2(frontLidStrip,sweepTime=0.5, dimRatio=0.9, onValue=Colors.RED )
centerPattern = ABFade( centerStoneLights, value=oscillator/20, a =Colors.RED, b=Colors.BLUE )
rainbowLeft = Rainbow(leftStoneLights,colorCycle=rbCycle, spread=rbs )
rainbowRight = Rainbow(rightStoneLights,colorCycle=1.1, spread=2.0 )
aglSpinner = Spinner(angleGaugeLights, onValue=Colors.RED, tail=0.42,period=0.49)

lsZ21 = Z21Adapted( lightSensor )
ls256 = lsZ21 * 256
csWheel = ColorWheel( ls256 )
main.panel.monitor( csWheel, description="Color Wheel based on light sensor" )
#csWheel.enableDbgOut = True

closedSpin = Spinner(angleGaugeLights,onValue=csWheel,period=3.49 )
centerSpin = Spinner(centerStoneLights)

sceneOpen.addPatterns( frontLidBlink(onValue="GREEN"), aglSpinner, rainbowLeft, rainbowRight )
sceneClosed.addPatterns( frontLidBlink(onValue="RED"), closedSpin, centerPattern, rainbowLeft, rainbowRight  )
sceneMoving.addPatterns( frontLidBlink(onValue="YELLOW"), centerSpin, aglSpinner )




#############################################################################
# Wrap up and launch : http://lumensalis.com/ql/h2Launch
sayAtStartup( "launch ..." )

main.launchProject( globals() )
