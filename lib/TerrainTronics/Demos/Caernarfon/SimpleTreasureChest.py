from ..DemoCommon import *

#############################################################################
main = MainManager.initOrGetManager()

sceneClosed = main.addScene( "closed" ) 
sceneOpen = main.addScene( "open" ) 
sceneMoving  = main.addScene( "moving" )

#############################################################################
# setup hardware
caernarfon = main.TerrainTronics.addCaernarfon( neoPixelCount=45 )
neoPixA = caernarfon.pixels 
neoPixB = caernarfon.initNeoPixOnServo(3,neoPixelCount=35)
ir = caernarfon.addIrRemote(codenames="dvd_remote")     
lidDrive = caernarfon.initServo( 1, "lidDrive", movePeriod=0.05 )

capTouch = main.adafruitFactory.addMPR121()
ranger = main.i2cFactory.addVL530lx(updateInterval=0.25)
magInputs = main.adafruitFactory.addAW9523()
lidClosedMag    = magInputs.addInput(1,"lidClosed")
lidOpenMag      = magInputs.addInput(2,"mag2")

rbCycle = main.addControlVariable( "rbColorCycle", startingValue=3.1, min=0.1, max=10.0, kind="TimeInSeconds" )
rbs = main.addControlVariable( "rbSpread", startingValue=0.6, min=0.1, max=3.0, kind=float )

#############################################################################
# setup neoPixel modules
pixOnCaernarfon         = neoPixA.single()
insideSingle            = neoPixA.single()
leftStoneLights         = neoPixA.ring(3)
centerStoneLights       = neoPixA.ring(7)
rightStoneLights        = neoPixA.ring(3)
frontLidStrip           = neoPixA.stick(8)
sceneIndicatorLights    = neoPixB.stick(8)
angleGaugeLights        = neoPixB.ring(12)

#############################################################################
# setup touch inputs
leftStoneTouch = capTouch.addInput( 1, "left" )
centerStoneTouch = capTouch.addInput( 2, "center" )
rightStoneTouch = capTouch.addInput( 4, "right" )
leftRimTouch = capTouch.addInput( 5, "left" )
centerRimTouch = capTouch.addInput( 6, "center" )
rightRimTouch = capTouch.addInput( 7, "right" )
bottomTouch = capTouch.addInput( 8, "right" )

#############################################################################
# setup lid
lid = Motion.ServoDoor(lidDrive, 
        closedPosition = 126,
        openPosition = 14,
        defaultSpeed= 12
)

fireOnRising( rightStoneTouch, lid.open )
fireOnRising( rightRimTouch, lid.close )
ir.onCode( "DOWN", lid.close )
ir.onCode( "UP", lid.open )

lid.opened.setScene( sceneOpen )
lid.closed.setScene( sceneClosed )
lid.opening.setScene( sceneMoving )
lid.closing.setScene( sceneMoving )

@ir.onCodeDef( "NEXT" )
def next(): main.scenes.switchToNextIn( ["closed","opening","open","closing"] )

#############################################################################
# setup LED patterns
oscillator2 = Oscillator.Oscillator( "o2", low = 0.3, high = 2, frequency = 0.1 )
oscillator = Oscillator.Oscillator( "sawtooth", low = 0, high = 10, frequency = oscillator2 )

frontLidStripPattern = Cylon2(frontLidStrip,sweepTime=0.5, dimRatio=0.9, onValue=LightValueRGB.RED )
centerPattern = PatternRLTest(  centerStoneLights, value=oscillator/20 )
rainbowLeft = Rainbow(leftStoneLights,colorCycle=rbCycle, spread=rbs ) #,whenOffset = 2.1 ),
rainbowRight = Rainbow(rightStoneLights,colorCycle=1.1, spread=2.0 )
agl = Spinner(angleGaugeLights, "agl", onValue=LightValueRGB.RED, tail=0.42,period=0.49)
def fsp( color ): return Blink( frontLidStrip, f"Blink{color}",  onTime=0.25, offTime=0.25, onValue = getattr(LightValueRGB,color) )

sceneOpen.addPatterns( fsp("GREEN"), agl, rainbowLeft, rainbowRight )
sceneClosed.addPatterns( fsp("RED"), centerPattern, rainbowLeft, rainbowRight  )
sceneMoving.addPatterns( fsp("YELLOW"), Spinner(centerStoneLights,"cspin"), agl )

