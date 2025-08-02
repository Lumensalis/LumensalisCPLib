from LumensalisCP.ImportProfiler import ImportProfiler
ImportProfiler.SHOW_IMPORTS = True

# ALWAYS START WITH "from LumensalisCP.Simple import *"
from LumensalisCP.Simple import * # http://lumensalis.com/ql/h2Start

#############################################################################
sayAtStartup( "start project" ) #  http://lumensalis.com/ql/h2Main
main2:MainManager = ProjectManager(
        profile=True,
        #  profileMemory=3
    ) 

main = getMainManager()

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
ir = caernarfon.addIrRemote(codenames="dvd_remote", refreshRate=5.0 )
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
timeOfFlightSensor = main.i2cFactory.addVL530lx(refreshRate=0.25)
vcnl4040 = main.adafruitFactory.addVCNL4040()

lightSensor = vcnl4040.light
proximitySensor = vcnl4040.proximity
vcnl4040.light_integration_time = 2
vcnl4040.proximity_integration_time = 2
main.panel.monitor( lightSensor )
main.panel.monitor( proximitySensor )

#############################################################################
sayAtStartup( "setup touch inputs" ) # http://lumensalis.com/ql/h2Touch
capTouch = main.adafruitFactory.addMPR121()
leftStoneTouch, centerStoneTouch, rightStoneTouch= capTouch.addInputs( 1, 2, 4 )
leftRimTouch, centerRimTouch, rightRimTouch= capTouch.addInputs( 5, 6, 7 )
bottomTouch = capTouch.addInput( 8 )

magInputs = main.adafruitFactory.addAW9523()
lidClosedMag    = magInputs.addInput(1)
lidOpenMag      = magInputs.addInput(2)

#############################################################################
sayAtStartup( "setup oscillators" ) # http://lumensalis.com/ql/h2Oscillators
oscillator2 = Oscillator.Oscillator( low = 0.3, high = 2, frequency = 0.1 )
oscillator = Oscillator.Oscillator(  low = 0, high = 10, frequency = oscillator2 )
oscillator.activate()
#############################################################################
sayAtStartup( "setup synth" )

audio = main.addI2SAudio(
    word_select=board.IO14,     # MAX98357 lrc:green
    bit_clock=board.IO13,       # MAX98357 bclk:yellow
    data=board.IO10,            # MAX98357 din:orange
)

testEffect = audio.effects.makeEffect() # filterMode=BAND_PASS)
testEffect.enableDbgOut = True

def updateTestEffect(source:Any=None, context:Optional[EvaluationContext]=None) -> None:
    #testEffect.filter.frequency = oscillator.value * 2000 + 100
    v = oscillator.latestValue /10
    testEffect.note.bend = v
    #testEffect.infoOut( "bending to %r", v )

oscillator.onChange( updateTestEffect  )

@addPeriodicTaskDef( interval=0.03, name="updateOscillator" )
def updateOscillator(context:EvaluationContext) -> None:
    oscillator.updateValue(context)

def touchNote(context:Optional[EvaluationContext]=None, a2:Optional[Any]=None, a3:Optional[Any]=None) -> Any:
    print( "in touchNote" )
    if testEffect.playing:
        print( "releasing note" )
        testEffect.stop()
    else:
        print( "startNote" )
        testEffect.start()

    return 42

print( f"touchNote = {touchNote}" )

# fireOnRising( leftRimTouch, do( touchNote ) )
dot = do( touchNote )
dot.enableDbgOut = True
#dot.name = "dot"

fireDot = fireOnRising( leftRimTouch, dot )
fireDot.enableDbgOut = True
leftRimTouch.enableDbgOut = True

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
# setup LED patterns : http://lumensalis.com/ql/h2Patterns
sayAtStartup( "setup patterns" )

frontLidBlink = PatternTemplate( Blink, frontLidStrip, onTime=0.25, offTime=0.25 )

frontLidStripPattern = Cylon2(frontLidStrip,sweepTime=0.5, dimRatio=0.9, onValue=Colors.RED )
centerPattern = ABFade( centerStoneLights, value=oscillator/20, a =Colors.RED, b=Colors.BLUE )
rainbowLeft = Rainbow(leftStoneLights,colorCycle=rbCycle, spread=rbs )
rainbowRight = Rainbow(rightStoneLights,colorCycle=1.1, spread=2.0 )
aglSpinner = Spinner(angleGaugeLights, onValue=Colors.RED, tail=0.42,period=0.49)

lsZ21 = Z21Adapted( lightSensor )
csWheel = ColorWheelZ1( lsZ21 )
main.panel.monitor( csWheel, description="Color Wheel based on light sensor" )
#csWheel.enableDbgOut = True

closedSpin = Spinner(angleGaugeLights,onValue=csWheel,period=3.49 )
centerSpin = Spinner(centerStoneLights)

sceneOpen.addPatterns( frontLidBlink(onValue="GREEN"), aglSpinner, rainbowLeft, rainbowRight )
#sceneClosed.addPatterns( frontLidBlink(onValue="RED"), closedSpin, centerPattern, rainbowLeft, rainbowRight  )
sceneClosed.addPatterns( closedSpin )
sceneMoving.addPatterns( frontLidBlink(onValue="YELLOW"), centerSpin, aglSpinner )

#############################################################################
# Wrap up and launch : http://lumensalis.com/ql/h2Launch
sayAtStartup( "launch ..." )
main.launchProject( globals() )

