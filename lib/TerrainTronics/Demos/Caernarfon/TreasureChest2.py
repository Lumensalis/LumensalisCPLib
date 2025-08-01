import gc
print( f"dir(gc)={dir(gc)}" )
#gc.threshold( 16384 )

# pylint: disable=wrong-import-position

from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl,pmc_gcManager,printElapsed

mlc = pmc_mainLoopControl

mlc.nextWaitPeriod = 0.0025
#gcm.setMinimumThreshold( 925000 )

#mlc.ENABLE_PROFILE = True
#gcm.minimumThreshold = 925000

#gcm.minimumThreshold = 425000

pmc_gcManager.setMinimumThreshold( 325000 )

printElapsed( "importing" )

if 1:
    mlc.ENABLE_PROFILE = True
    pmc_gcManager.PROFILE_MEMORY = False
    pmc_gcManager.PROFILE_MEMORY_NESTED = False
    pmc_gcManager.PROFILE_MEMORY_ENTRIES = False
    
    
from LumensalisCP.Demo.DemoCommon import *
from LumensalisCP.Lights.ProxyLights import *
from LumensalisCP.Triggers.Timer import PeriodicTimer, addPeriodicTaskDef
from LumensalisCP.Behaviors.Motion import ServoDoor
from LumensalisCP.Lights.TestPatterns import *

from LumensalisCP.pyCp.importlib import reload
import LumensalisCP.Main.ProfilerRL
import TerrainTronics.Demos.Caernarfon.TreasureChest2RL
from . import TreasureChest2RL


printElapsed( "getting manager" )
main = MainManager.initOrGetManager()

def reloadTreasureChest():
    print( f"reloading ")

    reload( LumensalisCP.Main.ProfilerRL )
    reload( TerrainTronics.Demos.Caernarfon.TreasureChest2RL )
    
    main.callLater( lambda: TerrainTronics.Demos.Caernarfon.TreasureChest2RL.printDump( main ) )


printElapsed( "setting up hardware" )

ENABLE_IR_REMOTE = False
scenes = main.scenes
capTouch = main.adafruitFactory.addMPR121()
magInputs =main.adafruitFactory.addAW9523()
caernarfon = main.TerrainTronics.addCaernarfon( neoPixelCount=45 )
pixels = caernarfon.pixels 
pixels2 = caernarfon.initNeoPixOnServo(3,neoPixelCount=35)

lidDrive = caernarfon.initServo( 1, "lidDrive", movePeriod=0.05 )        
if ENABLE_IR_REMOTE:
    ir = caernarfon.addIrRemote()            
ranger = main.i2cFactory.addVL530lx(refreshRate=0.25)

## setup Touch inputs
capTouch.enableDbgOut = True
leftStoneTouch = capTouch.addInput( 1, "left" )
centerStoneTouch = capTouch.addInput( 2, "center" )
rightStoneTouch = capTouch.addInput( 4, "right" )
leftRimTouch = capTouch.addInput( 5, "left" )
centerRimTouch = capTouch.addInput( 6, "center" )
rightRimTouch = capTouch.addInput( 7, "right" )
bottomTouch = capTouch.addInput( 8, "right" )

## setup NeoPixels

pixOnCaernarfon = pixels.nextNLights(1)
insideSingle = pixels.nextNLights(1)
leftStoneLights = pixels.nextNLights(3)
centerStoneLights = pixels.nextNLights(7)
rightStoneLights = pixels.nextNLights(3)
frontLidStrip = pixels.nextNLights(8)
sceneIndicatorLights = pixels2.nextNLights(8)
angleGaugeLights = pixels2.nextNLights(12)

# setup inputs
lidClosedMag = magInputs.addInput(1,"lidClosed")
lidOpenMag = magInputs.addInput(2,"mag2")

# dmx
dmxTestRGB = main.dmx.addRGBInput( "color", 1 )
dmxTestDimmer = main.dmx.addDimmerInput( "dimmer", 4 )
dmxLid = main.dmx.addDimmerInput( "lid", 6 )
dmxEnable = main.dmx.addDimmerInput( "enable", 7 )

# setup Scenes     
sceneClosed = main.addScene("closed")
sceneOpen = main.addScene("open")
sceneOpening = main.addScene("opening")
sceneClosing = main.addScene("closing")

sceneA = main.addScene("A")
sceneB = main.addScene("B")
sceneC = main.addScene("C")
sceneD = main.addScene("D")

lid = ServoDoor(lidDrive, 
        closedPosition = 126,
        openPosition = 14,
        defaultSpeed= 12,
)

printElapsed( "parsing demo class" )
        
class TreasureChest( DemoBase ):

        
    def setupTouch(self):
                        
            #touched = Trigger("touched")
            #touched.enableDbgOut = True
            
            #@touched.addActionDef()
            def onTouched(**kwds):
                if leftStoneTouch :
                    self.openLid()
                #elif bottomTouch:
                #    print( f"reloading ")
                #    reload( TestPatternsRL )
                elif  centerRimTouch:
                    self.closeLid()
                elif rightStoneTouch:
                    self.main.scenes.currentScene = "dmxRemote"
                elif centerStoneTouch:
                    lidDrive.stop()
                    
                print( f"TOUCHED!!! { capTouch.touchedInputs}" )
            
            @fireOnTrueDef( centerStoneTouch )
            def rl():
                reloadTreasureChest()

            @fireOnTrueDef( bottomTouch )
            def rl():
                reloadTreasureChest( )
            
            @fireOnTrueDef( rightStoneTouch )
            def _(): self.closeLid()

            #@fireOnTrueDef( leftStoneTouch )
            #def _(): self.openLid()

            @fireOnTrueDef( leftStoneTouch )
            def _():
                sName = scenes.currentScene.name
                nextScene = dict(A="B",B="C",C="D",D="A").get(sName,"B")
                print( f"switch from scene {sName} to {nextScene}" )
                scenes.currentScene = nextScene 
                

            print( f"capTouch.inputs = {capTouch.inputs}")
            #touched.fireOnSourcesSet(*capTouch.inputs )
            
            def onUnusedTouch( unused=0, context=None ):
                activePins = []
                touched = capTouch.lastTouched
                for pin in range( capTouch.MPR121_PINS ):
                    if touched & (1 << pin):
                        activePins.append(pin)
                print( f"Unused Touch, touched={touched:X} pins = { ",".join([repr(pin) for pin in activePins])}")
            
            capTouch.onUnused( onUnusedTouch )
            
    def setupLights(self):
        if False:
            
            def blendWith( color:RGB, ratio:ZeroToOne ):
                def blended( light:Light, context: UpdateContext ):
                    return color.fadeTowards( light.getRGB(), ratio )
                return blended
            
            self.leftBlueLights = ProxyRGBLightsCallbackSource( 
                    leftStoneLights,  blendWith(LightValueRGB.BLUE, 0.45 ) )

            self.rightGreenLights = ProxyRGBLightsCallbackSource( 
                    rightStoneLights,  blendWith(LightValueRGB.GREEN, 0.25 ) )
        
              
    def setupLid(self):
        #####################################################################
        
        #####################################################################
        sceneManager = self.main.scenes
        
        @fireOnTrueDef( rising( lidOpenMag == True ) )
        def lidIsOpened():
            print( f"lidOpen!!!")
            #lidDrive.stop()
            #sceneManager.currentScene = "open"
            
            
        @fireOnTrueDef( rising( lidClosedMag == True ) )
        def lidIsClosed(**kwargs):
            print( f"lidClosed!!! {kwargs}")
            #lidDrive.stop()
            #sceneManager.currentScene = "closed"

        #self.magInputs.enableDbgOut = True
        #self.lidClosedMag.enableDbgOut = True

    def  lidArrived(self):
        
        print( "lid arrived, turning servo off" )
        if scenes.currentScene.name == "dmxRemote": return
        
        if lidDrive.lastSetAngle == self.lidClosedPosition:
            scenes.currentScene = "closed"
        elif self.lidDrive.lastSetAngle == self.lidOpenPosition:
            self.main.scenes.currentScene = "open"
            
        self.lidDrive.set( None )

    def closeLid(self):
        if self.main.scenes.currentScene.name == "dmxRemote": return
        self.main.scenes.setScene("closing")
        lid.close()
        #lidDrive.moveTo(lidClosedPosition,self.lidCloseSpeed)

    def openLid(self):
        if self.main.scenes.currentScene.name == "dmxRemote": return
        self.main.scenes.setScene("opening")
        lid.open()
        #lidDrive.moveTo(self.lidOpenPosition,self.lidOpenSpeed)
            
    def jogLid(self, delta):
        newAngle = self.lidDrive.lastSetAngle + delta
        print( f"lid to {newAngle}")
        self.lidDrive.set(newAngle)
            
    #########################################################################
    def setupRemote(self):
        #ir = self.ir = self.caernarfon.addIrRemote()
        

        sceneManager = self.main.scenes
        self.nextSceneDict =  dict(
                closed = "opening",
                opening = "open",
                open = "closing",
                closing = "closed",
            )
        
        @ir.onCodeDef( "NEXT" )
        def next():
            newSceneName = self.nextSceneDict.get( sceneManager.currentScene.name, None )
            if newSceneName is not sceneManager.currentScene.name:
                print( f"switching to scene {newSceneName}")
                sceneManager.setScene( newSceneName )
        
        ir.onCode( "CH-", self.closeLid )
        ir.onCode( "CH+", self.openLid )
        
        @ir.onCodeDef( "VOL+" )
        def jogLidUp(): self.jogLid(-1)

        @ir.onCodeDef( "VOL-" )
        def jogLidDown(): self.jogLid(1)

        @ir.onCodeDef( "CH" )
        def dmxRemote(): 
            sceneManager.setScene( "dmxRemote" )
        

    def setupChest(self):

        main = self.main

        #####################################################################
        # Add a CaernarfonCastle
        #caernarfon = main.TerrainTronics.addCaernarfon( neoPixelCount=45 )
        self.caernarfon = caernarfon

        self.main.scenes.enableDbgOut = True
        

        self.enableStatsPrint = False
        self.setupLights()
        self.setupLid()
        self.setupTouch()
        if ENABLE_IR_REMOTE:
            self.setupRemote()

        self.dmx = main.dmx
        
        def rChannel(): return randint(0,64)
        def randomRGB(): return (rChannel() << 16) + (rChannel() << 8) +  rChannel()


        #frontLidStripPattern = Cylon2(self.frontLidStrip, onValue=randomRGB )
        
        frontLidStripPattern = Gauge(frontLidStrip, name="RangeGauge",  )
        red = LightValueRGB.RED
        def gaugeOnValue( context:EvaluationContext = None,**kwargs):
            return red.fadeTowards(RGB.toRGB( wheel1( main.when/3.5)), frontLidStripPattern.value)
        frontLidStripPattern.onValue = gaugeOnValue
        
        
        #self.sceneIndicatorLights 
        #self.angleGaugeLights 
        anglePattern = Gauge(angleGaugeLights, name="AngleGauge", onValue=LightValueRGB.BLUE )
        
        
        rangeDump = dict( rMin = 99999, rMax = 0, rMaxB = 1, rMaxBCap=2192, rCount = 0 )
        
        def updateCylonColor(context:Optional[UpdateContext]=None, **kwargs):
            
            range = ranger.range.getValue(context=context) 
            showDump = ((rangeDump['rCount'] % 10) == 0)
            rangeDump['rCount'] += 1
            if range > rangeDump['rMax']: 
                rangeDump['rMax'] = range
                showDump = True
            if range > rangeDump['rMaxB'] and range < rangeDump['rMaxBCap']: 
                rangeDump['rMaxB'] = range
                showDump = True
            if range < rangeDump['rMin']:
                rangeDump['rMin'] = range
                showDump = True
            
            #sweepTime = max(0.2, min( ( range / rangeDump['rMaxB'] ) *5.0, 5.0 ) )
            #rangeDump['sweepTime'] = sweepTime
            #frontLidStripPattern.sweepTime = sweepTimed
            rangeRatio  = range / rangeDump['rMaxB']
            rangeDump['rangeRatio'] = rangeRatio
            frontLidStripPattern.set( rangeRatio, context=context )
            
            if showDump and False:
                print( f"range = {range}, {rangeDump}")
            
        #sceneOpen.addTask( updateCylonColor, period=0.35 )
        #sceneClosed.addTask( updateCylonColor, period=0.35 )
        
        def sawTooth(context=None,when=None):
            return divmod((context or main.getContext()).when, 2.5)[1]/7.0
            #return divmod(main.getContext().when, 2.5.0)[1]/7.0
        
        rbcc, rbs = 3.1, 0.6
        patterns = [
            #Rainbow(self.leftBlueLights,colorCycle=rbcc, spread=rbs ), #,whenOffset = 2.1 ),
            #Rainbow(self.rightGreenLights,colorCycle=rbcc, spread=rbs ),
            
            Rainbow(leftStoneLights,colorCycle=rbcc, spread=rbs ), #,whenOffset = 2.1 ),
            Rainbow(rightStoneLights,colorCycle=1.1, spread=2.0 ),
            
            #Random( self.centerStoneLights, duration = 0.2, intermediateRefresh=0.05 ),
            #Rainbow( centerStoneLights, colorCycle=3.5, spread=1),
            PatternRLTest(  centerStoneLights, value=sawTooth ),
            #Blink(insideSingle,
            #      onValue=randomRGB,
            #      onTime=lambda:randomZeroToOne() * 2.5,
            #      offValue=randomRGB,
            #      offTime=lambda:randomZeroToOne() *0.3 ,
            #      intermediateRefresh = 0.1
            #      ),
            
            #anglePattern
        ]
        
        if 1:
            sceneOpen.addPatterns( frontLidStripPattern, *patterns )
            #sceneClosed.addPatterns( Cylon2( frontLidStrip, sweepTime=0.15,onValue="RED"), *patterns )
            sceneClosed.addPatterns( *patterns )
            sceneColors = dict(
                    open=LightValueRGB.BLUE,
                    closed=LightValueRGB.GREEN,
                    opening = RGB( 1, 1, 0 ),
                    closing = RGB( 0, 1, 1 ),
                )
            sceneOpening.addPatterns( *patterns )
            sceneClosing.addPatterns( *patterns )
        #lidSpan = self.lidOpenPosition - self.lidClosedPosition 
        
        sceneA.addPatterns( patterns[0] )
        sceneB.addPatterns( *patterns )
        #####################################################################
        dmxRemote = main.addScene("dmxRemote")
        dmxRemote.addRule( pixels[1], dmxTestRGB )

        dmxRemote.addPatterns(
            Rainbow( centerStoneLights, colorCycle=dmxTestDimmer*5.0),
            Blink( leftStoneLights, onValue=dmxTestRGB, offTime=0.2 ),
            Gauge( frontLidStrip, "dimmer", value=dmxTestDimmer, onValue=dmxTestRGB ),
        )
        
        dmxRemote.addRule( lidDrive, dmxLid * lid.span + lid.closedPosition )
        
        @fireOnTrueDef( rising( dmxEnable > 0.9 ) )
        def enableDMX(**kwargs):
            print( "enableDMX...")
            scenes.currentScene = dmxRemote

        @fireOnTrueDef( rising( dmxEnable < 0.1 ) )
        def disableDMX(**kwargs):
            print( "disableDMX...")
            scenes.currentScene = "closing"
            
        
        #####################################################################
        
        dmxTestDimmer.enableDbgOut = True
        dmxTestRGB.enableDbgOut = True
        dmxLid.enableDbgOut = True
        dmxEnable.enableDbgOut = True
        
        def updateStuff( context=None, **kwargs ):
            context = context or self.main.latestContext
            
            #openRatio = (
            #    (self.lidDrive.lastSetAngle - lid.closedPosition) / lidSpan
            #)
            
            anglePattern.set( lid.openRatio, context )
            anglePattern.refresh( context=context )
            
            if main.scenes.currentScene is not None:
                sceneColor = sceneColors.get( scenes.currentScene.name, LightValueRGB.WHITE )
            else:
                sceneColor = LightValueRGB.BLACK
            
            #print( f"openRatio={openRatio} for {self.lidDrive.lastSetAngle}, sceneColor = {sceneColor} for {self.main.scenes.currentScene}" )
            sceneIndicatorLights[0] = sceneColor
            sceneIndicatorLights[1] = LightValueRGB.GREEN if lidClosedMag.value else LightValueRGB.BLACK
            sceneIndicatorLights[2] = LightValueRGB.GREEN if lidOpenMag.value else LightValueRGB.BLACK
            sceneIndicatorLights[3] = LightValueRGB.GREEN if leftRimTouch.value else LightValueRGB.BLACK
            sceneIndicatorLights[4] = LightValueRGB.GREEN if centerRimTouch.value else LightValueRGB.BLACK
            sceneIndicatorLights[5] = LightValueRGB.GREEN if rightRimTouch.value else LightValueRGB.BLACK
            sceneIndicatorLights[6] = LightValueRGB.GREEN if bottomTouch.value else LightValueRGB.BLACK

            pixels.refresh()
            pixels2.refresh()
            if self.enableStatsPrint:
                print( f"{main.latestContext.updateIndex}@{main.when:.3f}  openRatio={openRatio} for {self.lidDrive.lastSetAngle}, sceneColor = {sceneColor} for {self.main.scenes.currentScene}" )

        @fireOnTrueDef( rising( rightRimTouch == True ) )
        def toggleStatsPrint(**kwargs):
            self.enableStatsPrint = not self.enableStatsPrint 
            print( f"self.enableStatsPrint = {self.enableStatsPrint}")
            
        #pt = PeriodicTimer( 0.1, manager=main.timers, name="updateStuff" )
        #pt.addAction( updateStuff )
        #pt.start()
        #main.addTask( updateStuff )
        
        dt = PeriodicTimer( interval=lambda : pmc_gcManager.printDumpInterval, manager=main.timers, name="dump" )
        
        @dt.addSimpleTaskDef( "printDumpPeriod" )
        def dump():
            #print( f"DUMPING at {main.newNow}" )
            #dt.restart( interval=TreasureChest2RL.printDumpInterval )
            TerrainTronics.Demos.Caernarfon.pmc_gcManager.printDump(main)
            #print( f"DUMPED at {main.newNow}" )
            #gc.collect()
        #dt.addAction( dump )
        #dt.start()

        #@addPeriodicTaskDef( "gc-collect", period=3.5, main=main )
        def gc_check(context=None, when=None):
            printElapsed( "gc_check" )
                    
        main.scenes.enableDbgOut = True
        print(f"sources = {sceneClosed.sources()}" )
      

    def setup(self):
        self.setupChest()
        
 
        @addPeriodicTaskDef( "gc-collect", period=lambda: pmc_gcManager.collectionCheckInterval, main=main )
        def runCollection(context=None, when=None):
            pmc_gcManager.runCollection(context,when, show=True)

        def firstGC():
            pmc_gcManager.runCollection(main.getContext(),main.when, force=True)
        main.callLater(firstGC)

        gc.disable()
    
def demoMain(*args,**kwds):
    printElapsed( "initializing demo" )
    demo = TreasureChest( *args, **kwds )
    printElapsed( "running  demo" )
    demo.run()