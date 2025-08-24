from LumensalisCP.Simple import * # http://lumensalis.com/ql/h2Start
#############################################################################
sayAtStartup( "start project" ) #  http://lumensalis.com/ql/h2Main

main = ProjectManager( "CilgerranFountain" , useWifi=True )
manualControl = main.addScene( ) 
waterWheel = main.addScene( ) 
shishiOdoshi = main.addScene( )

# add devices
cilgerran = main.TerrainTronics.addCilgerran(withMotor=True,ledCount=6)
fountainTurret = cilgerran.motor
fountainTurret.minSpeed = 0.35
fountainChannels = cilgerran.ledSource.nextNLights(2) # skip 0/1 - reserved for fountain controls
cilLeds = cilgerran.ledSource.nextNLights(4)
fountainFlow = fountainChannels[0]

# setup tunables
rotateTimeBetweenPositions = main.tunables.addSeconds( 2.6 )
rotationSpeedBetweenPositions = main.tunables.addZeroToOne( 0.9 )

# setup panel controls - will be available in the UI
ui = main.panel
flowRate            = ui.addZeroToOne(      0.1, "fountain pump flow rate")
motorSpeed          = ui.addPlusMinusOne(   "manual turret rotation speed" )
manualSpeedControl  = ui.addSwitch(         "enable manual speed control" )
clBlinkBrightness   = ui.addZeroToOne(      0.5, "brightness for blinking LEDs")
rotateDuration      = ui.addSeconds(        2.6, "rotation duration", min=0,max=5)
rotateSpeed         = ui.addZeroToOne(      0.6, "rotation speed")

jogLeft   = ui.addTrigger( "rotate left", action= do( fountainTurret.spin, rotateSpeed*-1, rotateDuration ) )
jogRight  = ui.addTrigger( "rotate right", action=do( fountainTurret.spin, rotateSpeed, rotateDuration ) )
toWheel   = ui.addTrigger( "rotate to wheel", scene=waterWheel )
toShishi  = ui.addTrigger( "rotate to shishi-odoshi", scene=shishiOdoshi )
toManual  = ui.addTrigger( "manual mode", scene=manualControl )

manualControl.addRule( fountainFlow, flowRate )
manualControl.addRule( fountainTurret.manualSpeed, motorSpeed )
manualControl.addRule( fountainTurret.manualOverride, manualSpeedControl )
manualControl.addPatterns(
    Blink(cilLeds,onTime=10.0, offTime=1.0,onValue=clBlinkBrightness), # blink leds on Cilgerran
)

waterWheel.onEnter( do( fountainFlow.set, 0.7 ) )
waterWheel.onChangeTo( shishiOdoshi, do( fountainTurret.spin, -rotationSpeedBetweenPositions, rotateTimeBetweenPositions ) )

shishiOdoshi.onEnter( do( fountainFlow.set, 0.4 ) )
shishiOdoshi.onChangeTo( waterWheel, do( fountainTurret.spin, rotationSpeedBetweenPositions, rotateTimeBetweenPositions ) )

main.launchProject( globals() )
