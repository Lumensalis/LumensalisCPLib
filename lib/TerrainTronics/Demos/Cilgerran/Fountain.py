from LumensalisCP.Simple import * # http://lumensalis.com/ql/h2Start
#############################################################################
sayAtStartup( "start project" ) #  http://lumensalis.com/ql/h2Main
main = ProjectManager( "TwinCastlesFountain" , useWifi=True )
actOne = main.addScene( ) 

caernarfon = main.TerrainTronics.addCaernarfon(  config="secondary",  neoPixelCount=40 )
cilgerran = main.TerrainTronics.addCilgerran()

fountainTurret = cilgerran.motor
# assign Cilgerran Castle output / LED channels
cilgerranChannels = cilgerran.ledSource
cilgerranChannels.enableDbgOut=True
cilgerranChannels.addLeds(6)
fountainChannels = cilgerranChannels.nextNLights(2) # skip 0/1 - reserved for fountain controls
cilLeds = cilgerranChannels.nextNLights(4)
#motorA,motorB = cilgerranChannels.nextNLights(2)

# assign NeoPixel modules
ringA = caernarfon.pixels.ring(16)  # 16 LED ring
stripA = caernarfon.pixels.strip(8) # followed by 8 LED strip

# setup panel controls - will be available in the UI
brightness = main.panel.addZeroToOne(1.0,description="Cilgerran Castle master brightness")
flowRate = main.panel.addZeroToOne(0.1, description="fountain pump flow rate")
rbSpeed = main.panel.addSeconds(0.5,min=0.1,max=10,  description="speed of change for Rainbow ring")
rpSpread = main.panel.addFloat("degree of color variation for Rainbow ring", startingValue=0.5,min=0.3,max=5.0,)
motorSpeed  = main.panel.addPlusMinusOne( description = "speed for Cilgerran motor" )
manualSpeedControl = main.panel.addSwitch( description="enable manual speed control" )
clBlinkBrightness = main.panel.addZeroToOne(0.5, description="brightness for blinking LEDs")


rotateDuration = main.panel.addSeconds(2.0,min=0,max=10, description="rotation duration")
rotateSpeed = main.panel.addZeroToOne(0.6, description="rotation speed")
jogLeft = main.panel.addTrigger( description="rotate left" )
jogRight = main.panel.addTrigger( description="rotate right" )

actOne.addRule( fountainChannels[0], flowRate )
actOne.addRule( cilgerranChannels.brightness, brightness )

#fountainTurret.setEnableDebugWithChildren( True )
setManualSpeed = actOne.addRule( fountainTurret.manualSpeed, motorSpeed )
setManualOverride = actOne.addRule( fountainTurret.manualOverride, manualSpeedControl )

main.panel.monitor(setManualSpeed)

jogLeft.addAction( do( fountainTurret.spin, rotateSpeed*-1, rotateDuration ))
jogRight.addAction( do( fountainTurret.spin, rotateSpeed, rotateDuration ))
# add LED patterns
rainbow = actOne.addPattern( Rainbow( ringA,  # rainbow on ring
                colorCycle=rbSpeed, 
                spread=rpSpread
        ) )

actOne.addPatterns(
        Blink(cilLeds,onTime=1.0, offTime=1.0,onValue=clBlinkBrightness), # blink leds on Cilgerran
        Rainbow(stripA, spread=3, colorCycle=3.0), # rainbow on strip
    )

main.launchProject( globals() )
