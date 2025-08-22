from LumensalisCP.Simple import * # http://lumensalis.com/ql/h2Start
#############################################################################
sayAtStartup( "start project" ) #  http://lumensalis.com/ql/h2Main
main = ProjectManager( "CilgerranFountain" , useWifi=True )
actOne = main.addScene( ) 

cilgerran = main.TerrainTronics.addCilgerran(withMotor=True,ledCount=6)

fountainTurret = cilgerran.motor
fountainTurret.minSpeed = 0.35
# assign Cilgerran Castle output / LED channels
fountainChannels = cilgerran.ledSource.nextNLights(2) # skip 0/1 - reserved for fountain controls
cilLeds = cilgerran.ledSource.nextNLights(4)

# setup panel controls - will be available in the UI
ui = main.panel
flowRate            = ui.addZeroToOne(      0.1, "fountain pump flow rate")
motorSpeed          = ui.addPlusMinusOne(   "manual turret rotation speed" )
manualSpeedControl  = ui.addSwitch(         "enable manual speed control" )
clBlinkBrightness   = ui.addZeroToOne(      0.5, "brightness for blinking LEDs")
rotateDuration      = ui.addSeconds(        2.6, "rotation duration", min=0,max=5)
rotateSpeed         = ui.addZeroToOne(      0.6, "rotation speed")
jogLeft             = ui.addTrigger(       "rotate left" )
jogRight            = ui.addTrigger(       "rotate right" )

actOne.addRule( fountainChannels[0], flowRate )
actOne.addRule( fountainTurret.manualSpeed, motorSpeed )
actOne.addRule( fountainTurret.manualOverride, manualSpeedControl )

jogLeft.addAction( do( fountainTurret.spin, rotateSpeed*-1, rotateDuration ))
jogRight.addAction( do( fountainTurret.spin, rotateSpeed, rotateDuration ))

# add LED patterns
actOne.addPatterns(
    Blink(cilLeds,onTime=1.0, offTime=1.0,onValue=clBlinkBrightness), # blink leds on Cilgerran
)

main.launchProject( globals() )
