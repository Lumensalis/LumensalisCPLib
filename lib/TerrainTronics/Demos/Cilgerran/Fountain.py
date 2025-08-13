from LumensalisCP.Simple import * # http://lumensalis.com/ql/h2Start
#############################################################################
sayAtStartup( "start project" ) #  http://lumensalis.com/ql/h2Main
main = ProjectManager( "TwinCastlesFountain" , useWifi=True )
actOne = main.addScene( ) 

caernarfon = main.TerrainTronics.addCaernarfon(  config="secondary",  neoPixelCount=40 )
cilgerran = main.TerrainTronics.addCilgerran()

# assign Cilgerran Castle output / LED channels
cilgerranChannels = cilgerran.ledSource
cilgerranChannels.addLeds(8)
fountainChannels = cilgerranChannels.nextNLights(2) # skip 0/1 - reserved for fountain controls
cilLeds = cilgerranChannels.nextNLights(4)
motorChannels = cilgerranChannels.nextNLights(2)

# assign NeoPixel modules
ringA = caernarfon.pixels.ring(16)  # 16 LED ring
stripA = caernarfon.pixels.strip(8) # followed by 8 LED strip

# setup panel controls - will be available in the UI
brightness = main.panel.addZeroToOne(startingValue=0.9, 
            description="Cilgerran Castle master brightness")
flowRate = main.panel.addZeroToOne(startingValue=0.1, 
            description="fountain pump flow rate")
rbSpeed = main.panel.addSeconds(startingValue=0.5,min=0.1,max=10, 
            description="speed of change for Rainbow ring")
rpSpread = main.panel.addFloat(startingValue=0.5,min=0.3,max=5.0,
            description="degree of color variation for Rainbow ring")

actOne.addRule( fountainChannels[0], flowRate )
actOne.addRule( cilgerranChannels.brightness, brightness )

# add LED patterns
rainbow = actOne.addPattern( Rainbow( ringA,  # rainbow on ring
                colorCycle=rbSpeed, 
                spread=rpSpread,
        ) )

actOne.addPatterns(
        Blink(cilLeds,onTime=1.0, offTime=1.0), # blink leds on Cilgerran
    )

main.launchProject( globals() )
