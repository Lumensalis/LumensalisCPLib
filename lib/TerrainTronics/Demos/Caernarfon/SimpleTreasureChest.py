from LumensalisCP.Simple import *

#############################################################################
# Get started
main = ProjectManager()

# setup three different scenes
sceneClosed, sceneOpen, sceneMoving= main.addScenes( 3 ) 
#setup 
rbCycle = main.addControlVariable( startingValue=3.1, min=0.1, max=10.0, kind="TimeInSeconds" )
rbs = main.addControlVariable( startingValue=0.6, min=0.1, max=3.0, kind=float )
handSafetyRange = main.addControlVariable( 300, min=10, kind="Millimeters" )

#############################################################################
# setup the Caernarfon Castle and attached hardware
caernarfon = main.TerrainTronics.addCaernarfon( neoPixelCount=45 )

timeOfFlightSensor = main.i2cFactory.addVL530lx(updateInterval=0.25)
handTooClose = timeOfFlightSensor.range < handSafetyRange

#############################################################################
# two NeoPixel chains on Caernarfon Castle...
neoPixA = caernarfon.pixels 
neoPixB = caernarfon.initNeoPixOnServo(3,neoPixelCount=35)

# setup neoPixel modules
firstTwoOnPixA  = neoPixA.nextNLights(2)
leftStoneLights         = neoPixA.ring(3)
centerStoneLights       = neoPixA.ring(7)
rightStoneLights        = neoPixA.ring(3)
frontLidStrip           = neoPixA.stick(8)
sceneIndicatorLights    = neoPixB.stick(8)
angleGaugeLights        = neoPixB.ring(12)

#############################################################################
# setup lid
magInputs = main.adafruitFactory.addAW9523()
lidClosedMag    = magInputs.addInput(1)
lidOpenMag      = magInputs.addInput(2)
lidServo = caernarfon.initServo( 1, movePeriod=0.05 )

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
# setup touch inputs
capTouch = main.adafruitFactory.addMPR121()
leftStoneTouch, centerStoneTouch, rightStoneTouch= capTouch.addInputs( 1, 2, 4 )
leftRimTouch, centerRimTouch, rightRimTouch= capTouch.addInputs( 5, 6, 7 )
bottomTouch = capTouch.addInput( 8 )

fireOnRising( rightStoneTouch, lid.open )
fireOnRising( rightRimTouch, lid.close )

#############################################################################
# setup remote control
ir = caernarfon.addIrRemote(codenames="dvd_remote")     
ir.onCode( "DOWN", do( lid.close ).unless( handTooClose ) )
ir.onCode( "UP", do( lid.open ) )
ir.onCode( "NEXT", do( main.scenes.switchToNextIn, ["sceneClosed","sceneOpening","sceneOpen","sceneClosing"] ) )

#############################################################################
# setup LED patterns
oscillator2 = Oscillator.Oscillator( low = 0.3, high = 2, frequency = 0.1 )
oscillator = Oscillator.Oscillator(  low = 0, high = 10, frequency = oscillator2 )

frontLidBlink = PatternTemplate( Blink, frontLidStrip, onTime=0.25, offTime=0.25 )

frontLidStripPattern = Cylon2(frontLidStrip,sweepTime=0.5, dimRatio=0.9, onValue=LightValueRGB.RED )
centerPattern = PatternRLTest(  centerStoneLights, value=oscillator/20 )
rainbowLeft = Rainbow(leftStoneLights,colorCycle=rbCycle, spread=rbs )
rainbowRight = Rainbow(rightStoneLights,colorCycle=1.1, spread=2.0 )
aglSpinner = Spinner(angleGaugeLights, onValue=LightValueRGB.RED, tail=0.42,period=0.49)
centerSpin = Spinner(centerStoneLights)

sceneOpen.addPatterns( frontLidBlink(onValue="GREEN"), aglSpinner, rainbowLeft, rainbowRight )
sceneClosed.addPatterns( frontLidBlink(onValue="RED"), centerPattern, rainbowLeft, rainbowRight  )
sceneMoving.addPatterns( frontLidBlink(onValue="YELLOW"), centerSpin, aglSpinner )

main.renameIdentifiables( globals() )