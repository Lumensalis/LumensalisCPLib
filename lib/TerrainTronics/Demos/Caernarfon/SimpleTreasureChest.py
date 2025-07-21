# ALWAYS START WITH "from LumensalisCP.Simple import *"
from LumensalisCP.Simple import * # http://lumensalis.com/ql/h2Start

#############################################################################
main = ProjectManager() #  http://lumensalis.com/ql/h2Main

# setup three different scenes : http://lumensalis.com/ql/h2Scenes
sceneClosed, sceneOpen, sceneMoving= main.addScenes( 3 ) 

# setup Control Inputs : http://lumensalis.com/ql/h2Controller
rbCycle = main.addControlVariable( startingValue=3.1, min=0.1, max=10.0, kind="TimeInSeconds" )
rbs = main.addControlVariable( startingValue=0.6, min=0.1, max=3.0, kind=float )
handSafetyRange = main.addControlVariable( 300, min=10, kind="Millimeters" )

#############################################################################
# HARDWARE : http://lumensalis.com/ql/h2Hardware

# setup the Caernarfon Castle : http://lumensalis.com/ql/h2Caernarfon
caernarfon = main.TerrainTronics.addCaernarfon( neoPixelCount=45 )
lidServo = caernarfon.initServo( 1, movePeriod=0.05 )
ir = caernarfon.addIrRemote(codenames="dvd_remote")     
neoPixA = caernarfon.pixels 
neoPixB = caernarfon.initNeoPixOnServo(3,neoPixelCount=35)
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
main.monitor( lightSensor, proximitySensor, ) # enableDbgOut = True )


# setup touch inputs : http://lumensalis.com/ql/h2Touch
capTouch = main.adafruitFactory.addMPR121()
leftStoneTouch, centerStoneTouch, rightStoneTouch= capTouch.addInputs( 1, 2, 4 )
leftRimTouch, centerRimTouch, rightRimTouch= capTouch.addInputs( 5, 6, 7 )
bottomTouch = capTouch.addInput( 8 )

magInputs = main.adafruitFactory.addAW9523()
lidClosedMag    = magInputs.addInput(1)
lidOpenMag      = magInputs.addInput(2)

#############################################################################
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
frontLidBlink = PatternTemplate( Blink, frontLidStrip, onTime=0.25, offTime=0.25 )

frontLidStripPattern = Cylon2(frontLidStrip,sweepTime=0.5, dimRatio=0.9, onValue=LightValueRGB.RED )
centerPattern = ABFade( centerStoneLights, value=oscillator/20, a =LightValueRGB.RED, b=LightValueRGB.BLUE )
rainbowLeft = Rainbow(leftStoneLights,colorCycle=rbCycle, spread=rbs )
rainbowRight = Rainbow(rightStoneLights,colorCycle=1.1, spread=2.0 )
aglSpinner = Spinner(angleGaugeLights, onValue=LightValueRGB.RED, tail=0.42,period=0.49)

#lightSensor.enableDbgOut = True
lsZ21 = Z21Adapted( lightSensor )
#lsZ21.enableDbgOut = True
ls256 = lsZ21 * 256
#ls256.enableDbgOut = True

csWheel = ColorWheel( ls256 )
# csWheel.enableDbgOut = True

closedSpin = Spinner(angleGaugeLights,onValue=csWheel,period=3.49 )
centerSpin = Spinner(centerStoneLights)

sceneOpen.addPatterns( frontLidBlink(onValue="GREEN"), aglSpinner, rainbowLeft, rainbowRight )
sceneClosed.addPatterns( frontLidBlink(onValue="RED"), closedSpin, centerPattern, rainbowLeft, rainbowRight  )
sceneMoving.addPatterns( frontLidBlink(onValue="YELLOW"), centerSpin, aglSpinner )

#############################################################################
# Wrap up and launch : http://lumensalis.com/ql/h2Launch
main.launchProject( globals() )
