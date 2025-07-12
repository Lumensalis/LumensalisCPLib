from . import SimpleTreasureChestRL
from ..DemoCommon import *

#############################################################################
main = MainManager.initOrGetManager()
scenes = main.scenes

sceneClosed = main.addScene( "closed" ) 
sceneOpen = main.addScene( "open" ) 
sceneOpening = main.addScene( "opening" ) 
sceneClosing = main.addScene( "closing")

#############################################################################
caernarfon = main.TerrainTronics.addCaernarfon( neoPixelCount=45 )
neoPixelsChannelA = caernarfon.pixels 
neoPixelsChannelB = caernarfon.initNeoPixOnServo(3,neoPixelCount=35)

pixOnCaernarfon         = neoPixelsChannelA.nextNLights(1)
insideSingle            = neoPixelsChannelA.nextNLights(1)
leftStoneLights         = neoPixelsChannelA.nextNLights(3)
centerStoneLights       = neoPixelsChannelA.nextNLights(7)
rightStoneLights        = neoPixelsChannelA.nextNLights(3)
frontLidStrip           = neoPixelsChannelA.nextNLights(8)
sceneIndicatorLights    = neoPixelsChannelB.nextNLights(8)
angleGaugeLights        = neoPixelsChannelB.nextNLights(12)

#############################################################################
capTouch = main.adafruitFactory.addMPR121()
capTouch.enableDbgOut = True

leftStoneTouch = capTouch.addInput( 1, "left" )
centerStoneTouch = capTouch.addInput( 2, "center" )
rightStoneTouch = capTouch.addInput( 4, "right" )
leftRimTouch = capTouch.addInput( 5, "left" )
centerRimTouch = capTouch.addInput( 6, "center" )
rightRimTouch = capTouch.addInput( 7, "right" )
bottomTouch = capTouch.addInput( 8, "right" )

#############################################################################

ranger = main.i2cFactory.addVL530lx(updateInterval=0.25)
gateFrontRange = ranger.range
foo = main.addIntermediateVariable("foo", 0)
fooRule = sceneClosed.addRule(  foo, 
        gateFrontRange / 20
    ).when( 
            gateFrontRange < 1000
    ).otherwise(
        TERM( 50 )
    )

#############################################################################

magInputs       = main.adafruitFactory.addAW9523()
lidClosedMag    = magInputs.addInput(1,"lidClosed")
lidOpenMag      = magInputs.addInput(2,"mag2")

lidDrive = caernarfon.initServo( 1, "lidDrive", movePeriod=0.05 )

lid = Motion.ServoDoor(lidDrive, 
        closedPosition = 126,
        openPosition = 14,
        defaultSpeed= 12,
        enableDbgOut=True
)

# setup touch actions
@fireOnRising( rightStoneTouch )
def open():
    print( "opening lid" )
    lid.open()
    
fireOnRising( rightRimTouch, lid.close )

    
def sawTooth(context=None,when=None):
    
    return divmod((context or main.getContext()).when, 2.5)[1]/7.0


#############################################################################
# setup LED patterns

frontLidStripPattern = Cylon2(frontLidStrip,sweepTime=0.5, dimRatio=0.9, onValue=LightValueRGB.RED )

rbCycle = main.addControlVariable( "rbColorCycle", startingValue=3.1, min=0.1, max=10.0, kind="TimeInSeconds" )
rbs = main.addControlVariable( "rbSpread", startingValue=0.6, min=0.1, max=3.0, kind=float )
rbs.set( 0.7 )
#rbcc, rbs = 3.1, 0.6
patterns = [
    Rainbow(leftStoneLights,colorCycle=rbCycle, spread=rbs ), #,whenOffset = 2.1 ),
    Rainbow(rightStoneLights,colorCycle=1.1, spread=2.0 ),
    PatternRLTest(  centerStoneLights, value=sawTooth ),
]

sceneOpen.addPatterns( frontLidStripPattern, *patterns )
sceneClosed.addPatterns( *patterns )
sceneOpening.addPatterns( *patterns )
sceneClosing.addPatterns( *patterns )
    
ENABLE_IR_REMOTE = False
if ENABLE_IR_REMOTE:
    ir = caernarfon.addIrRemote()     
        
    ir.onCode( "CH-", lid.close )
    ir.onCode( "CH+", lid.open )

    @ir.onCodeDef( "NEXT" )
    def next():
        scenes.switchToNextIn( ["closed","opening","open","closing"] )
    
    @ir.onCodeDef( "VOL+" )
    def jogLidUp(): lid.jog(-1)

    @ir.onCodeDef( "VOL-" )
    def jogLidDown(): lid.jogLid(1)


web = main.addBasicWebServer()

#############################################################################
class TreasureChest( DemoBase ):
    def setup(self):
        SimpleTreasureChestRL.TreasureChest_finishSetup(self)
 
#############################################################################
def demoMain(*args,**kwds):
    demo = TreasureChest( *args, **kwds )
    demo.run()
