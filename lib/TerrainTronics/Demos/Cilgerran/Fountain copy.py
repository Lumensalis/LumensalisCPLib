from LumensalisCP.Simple import * # http://lumensalis.com/ql/h2Start

#############################################################################
sayAtStartup( "start project" ) #  http://lumensalis.com/ql/h2Main
main = ProjectManager(  "TwinCastlesFountain",
                      #useWifi=False,
                      useWifi=True,
                       #profile=True, profileMemory=3   
            )

scene = main.addScene( ) 

NEO_PIXEL_COUNT = 40

caernarfon = main.TerrainTronics.addCaernarfon( 
                config="secondary", 
                neoPixelCount=NEO_PIXEL_COUNT,
                refreshRate = 0.05
        )

cilgerran = main.TerrainTronics.addCilgerran()

leds = cilgerran.ledSource
leds.addLeds(8)

firstTwo = leds.nextNLights(2)
secondTwo = leds.nextNLights(2)
lastFour = leds.nextNLights(4)

brightness = main.panel.addZeroToOne(startingValue=0.9)
f0 = main.panel.addZeroToOne(startingValue=0.1)
f1 = main.panel.addZeroToOne(startingValue=0.1)
f2 = main.panel.addZeroToOne(startingValue=0.1)
f3 = main.panel.addZeroToOne(startingValue=0.1)
f4 = main.panel.addZeroToOne(startingValue=0.1)
f5 = main.panel.addZeroToOne(startingValue=0.9)
f6 = main.panel.addZeroToOne(startingValue=0.6)
f7 = main.panel.addZeroToOne(startingValue=0.6)
rbSpeed = main.panel.addSeconds(startingValue=0.5,min=0.1,max=10)
rpSpread = main.panel.addFloat(startingValue=0.5,min=0.3,max=5.0)
#ir = caernarfon.addIrRemote()
ringBowLeds = caernarfon.pixels.ring(16)

blinky, rbow = scene.addPatterns(
    Blink(secondTwo,onTime=1.0, offTime=1.0),
    #Blink(firstTwo,onTime=3.3, offTime=3.3),
    #Cylon(firstFour, sweepTime=0.7),
    #Blink(lastFour,onTime=15.0, offTime=1.5),
    Rainbow(ringBowLeds, colorCycle=rbSpeed, spread=rpSpread, refreshRate=0.05),
)
leds.brightness = 1
rbow.enableDbgOut = True

BRIGHTNESS_SWEEP_SECONDS = 10.0
#@addSceneTask( scene, period = 0.1 )
def brighten():
    brightness = (
        divmod( main.when, BRIGHTNESS_SWEEP_SECONDS )[1]
            / BRIGHTNESS_SWEEP_SECONDS ) #/ 10.0
    
    # print( f"brightness = {brightness}")
    leds.brightness = brightness

#@addSceneTask( scene, refreshRate = 0.1 )
def setLeds() -> None:
    leds.brightness = brightness.value
    leds[0].setValue( f0.value )
    #leds[1].setValue( f1.value )
    #leds[2].setValue( f2.value )
    #leds[3].setValue( f3.value )
    #leds[4].setValue( f4.value )
    #leds[5].setValue( f5.value )    
    #leds[5].setValue( f6.value )
    leds[6].setValue( f7.value )

#scene.enableDbgOut = True
tLeds = scene.addTask(task=setLeds, refreshRate = 0.1  )
#tLeds.enableDbgOut = True
            

leds.enableDbgOut = True
fountainFlow = leds[0]
fountainFlow.enableDbgOut = True
cil7 = leds[7]
cil7.enableDbgOut = True

# @addSceneTask( scene, refreshRate = 1.0 )
def showBattery():
    #b = leds.brightness
    #print( f"battery = {cilgerran.batteryMonitor.value}, brightness={b}")
    ledStr = ",".join( [f"{led.sourceIndex}:{led.value:0.2f}:{led.dutycycle}" for led in leds])
    print( f'bat:{cilgerran.batteryMonitor.value}, bright:{leds.brightness}, leds={ledStr}')
    #leds.brightness = b

tBattery  = scene.addTask(task=showBattery, refreshRate = 3.0  )
#tBattery.enableDbgOut = True


main.launchProject( globals() )