from ..DemoCommon import *
from LumensalisCP.Lights.ProxyLights import *
from LumensalisCP.Triggers.Timer import PeriodicTimer

class TreasureChest( DemoBase ):

    def setupTouch(self):
            self.capTouch = capTouch = self.main.adafruitFactory.addMPR121()
            capTouch.enableDbgOut = True
            self.leftStoneTouch = capTouch.addInput( 1, "left" )
            self.centerStoneTouch = capTouch.addInput( 2, "center" )
            self.rightStoneTouch = capTouch.addInput( 4, "right" )
            self.leftRimTouch = capTouch.addInput( 5, "left" )
            self.centerRimTouch = capTouch.addInput( 6, "center" )
            self.rightRimTouch = capTouch.addInput( 7, "right" )
            self.bottomTouch = capTouch.addInput( 8, "right" )

                        
            touched = Trigger("touched")
            touched.enableDbgOut = True
            
            @touched.addActionDef()
            def onTouched(**kwds):
                if self.leftStoneTouch or self.bottomTouch:
                    self.openLid()
                elif self.rightStoneTouch or self.centerRimTouch:
                    self.closeLid()
                elif self.centerStoneTouch:
                    self.lidDrive.stop()
                    
                print( f"TOUCHED!!! { capTouch.touchedInputs}" )
                    
            print( f"capTouch.inputs = {capTouch.inputs}")
            touched.fireOnSourcesSet(*capTouch.inputs )
            
            def onUnusedTouch( unused=0, context=None ):
                activePins = []
                touched = capTouch.lastTouched
                for pin in range( capTouch.MPR121_PINS ):
                    if touched & (1 << pin):
                        activePins.append(pin)
                print( f"Unused Touch, touched={touched:X} pins = { ",".join([repr(pin) for pin in activePins])}")
            
            capTouch.onUnused( onUnusedTouch )
            
    def setupLights(self):
        self.pixels = pixels = self.caernarfon.pixels 

        self.pixOnCaernarfon = pixels.nextNLights(1)
        self.insideSingle= pixels.nextNLights(1)
        self.leftStoneLights = pixels.nextNLights(3)
        self.centerStoneLights = pixels.nextNLights(7)
        self.rightStoneLights = pixels.nextNLights(3)
        self.frontLidStrip = pixels.nextNLights(8)
        
        def blendWith( color:RGB, ratio:ZeroToOne ):
            def blended( light:LightBase, context: UpdateContext ):
                return color.fadeTowards( light.getRGB(), ratio )
            return blended
        
        self.leftBlueLights = ProxyRGBLightsCallbackSource( 
                self.leftStoneLights,  blendWith(LightValueRGB.BLUE, 0.45 ) )

        self.rightGreenLights = ProxyRGBLightsCallbackSource( 
                self.rightStoneLights,  blendWith(LightValueRGB.GREEN, 0.25 ) )
        
        self.pixels2 = pixels2 = self.caernarfon.initNeoPixOnServo(3,neoPixelCount=35)
        
        self.sceneIndicatorLights = pixels2.nextNLights(8)
        self.angleGaugeLights = pixels2.nextNLights(12)
        
    def setupLid(self):
        #####################################################################
        
        self.magInputs = magInputs = self.main.adafruitFactory.addAW9523()
        
        self.lidClosedMag = magInputs.addInput(1,"lidClosed")
        #self.lidClosedMag.enableDbgOut = True
        self.lidOpenMag = magInputs.addInput(2,"mag2")
        
        #####################################################################
        # gate movement
        self.lidClosedPosition = 126
        self.lidOpenPosition = 14
        self.lidOpenSpeed = 12
        self.lidCloseSpeed = 12
        self.lidCloseSpeed = 12
        
        self.lidDrive = lidDrive = self.caernarfon.initServo( 1, "lidDrive", movePeriod=0.05 )
        lidDrive.set(self.lidClosedPosition)
        lidDrive.onMoveComplete( self.lidArrived )

        sceneManager = self.main.scenes
        
        
        @fireOnTrue( rising( self.lidOpenMag == True ) )
        def lidIsOpened(**kwargs):
            print( f"lidOpen!!!")
            #lidDrive.stop()
            #sceneManager.currentScene = "open"
            
            
        @fireOnTrue( rising( self.lidClosedMag == True ) )
        def lidIsClosed(**kwargs):
            print( f"lidClosed!!!")
            #lidDrive.stop()
            #sceneManager.currentScene = "closed"

        #self.magInputs.enableDbgOut = True
        #self.lidClosedMag.enableDbgOut = True

    def  lidArrived(self):
        print( "lid arrived, turning servo off" )
        if self.lidDrive.lastSetAngle == self.lidClosedPosition:
            self.main.scenes.currentScene = "closed"
        elif self.lidDrive.lastSetAngle == self.lidOpenPosition:
            self.main.scenes.currentScene = "open"
            
        self.lidDrive.set( None )

    def closeLid(self):
        self.main.scenes.setScene("closing")
        self.lidDrive.moveTo(self.lidClosedPosition,self.lidCloseSpeed)

    def openLid(self):
        self.main.scenes.setScene("opening")
        self.lidDrive.moveTo(self.lidOpenPosition,self.lidOpenSpeed)
            
    def jogLid(self, delta):
            newAngle = self.lidDrive.lastSetAngle + delta
            print( f"lid to {newAngle}")
            self.lidDrive.set(newAngle)
            
    #########################################################################
    def setupRemote(self):
        ir = self.ir = self.caernarfon.addIrRemote()
        

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

    def setup(self):

        main = self.main

        #####################################################################
        # Add a CaernarfonCastle
        caernarfon = main.TerrainTronics.addCaernarfon( neoPixelCount=45 )
        self.caernarfon = caernarfon

        self.main.scenes.enableDbgOut = True
        
        sceneOpen = main.addScene("open")
        sceneOpening = main.addScene("opening")
        sceneClosed = main.addScene("closed")
        sceneClosing = main.addScene("closing")

        self.enableStatsPrint = False
        #self.setupDisplay()
        self.setupLights()
        self.setupLid()
        self.setupTouch()
        self.setupRemote()

        def rChannel(): return randint(0,64)
        def randomRGB(): return (rChannel() << 16) + (rChannel() << 8) +  rChannel()


        #frontLidStripPattern = Cylon2(self.frontLidStrip, onValue=randomRGB )
        
        frontLidStripPattern = Gauge(self.frontLidStrip, name="RangeGauge",  )
        red = LightValueRGB.RED
        def gaugeOnValue( context:UpdateContext = None,**kwargs):
            return red.fadeTowards(LightValueRGB.toRGB( wheel1( main.when/3.5)), frontLidStripPattern.value)
        frontLidStripPattern.onValue = gaugeOnValue
        
        
        #self.sceneIndicatorLights 
        #self.angleGaugeLights 
        anglePattern = Gauge(self.angleGaugeLights, name="AngleGauge", onValue=LightValueRGB.BLUE )
        
        ranger = main.i2cFactory.addVL530lx(updateInterval=0.25)
        rangeDump = dict( rMin = 99999, rMax = 0, rMaxB = 1, rMaxBCap=2192, rCount = 0 )
        
        def updateCylonColor(context:UpdateContext=None, **kwargs):
            
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
            #frontLidStripPattern.sweepTime = sweepTime
            rangeRatio  = range / rangeDump['rMaxB']
            rangeDump['rangeRatio'] = rangeRatio
            frontLidStripPattern.set( rangeRatio, context=context )
            
            if showDump and False:
                print( f"range = {range}, {rangeDump}")
            
        sceneOpen.addTask( updateCylonColor, period=0.025 )
        sceneClosed.addTask( updateCylonColor, period=0.025 )
        
        rbcc, rbs = 3.1, 0.6
        patterns = [
            Rainbow(self.leftBlueLights,colorCycle=rbcc, spread=rbs ), #,whenOffset = 2.1 ),
            Rainbow(self.rightGreenLights,colorCycle=rbcc, spread=rbs ),
            #Random( self.centerStoneLights, duration = 0.2, intermediateRefresh=0.05 ),
            Rainbow( self.centerStoneLights, colorCycle=3.5, spread=1),
            Blink(self.insideSingle,
                  onValue=randomRGB,
                  onTime=lambda:randomZeroToOne() * 2.5,
                  offValue=randomRGB,
                  offTime=lambda:randomZeroToOne() *0.3 ,
                  intermediateRefresh = 0.1
                  ),
            frontLidStripPattern,
            anglePattern
        ]
        
        sceneOpen.addPatterns( *patterns )
        sceneClosed.addPatterns( *patterns )
        sceneColors = dict(
                open=LightValueRGB.BLUE,
                closed=LightValueRGB.GREEN,
                opening = RGB( 1, 1, 0 ),
                closing = RGB( 0, 1, 1 ),
            )
        lidSpan = self.lidOpenPosition - self.lidClosedPosition 

        #####################################################################
        def updateStuff( context=None, **kwargs ):
            context = context or self.main.latestContext
            
            openRatio = (
                (self.lidDrive.lastSetAngle - self.lidClosedPosition) / lidSpan
            )
            
            anglePattern.set( openRatio, context )
            anglePattern.refresh( context=context )
            
            sceneColor = sceneColors.get( self.main.scenes.currentScene.name, LightValueRGB.WHITE )
            
            #print( f"openRatio={openRatio} for {self.lidDrive.lastSetAngle}, sceneColor = {sceneColor} for {self.main.scenes.currentScene}" )
            self.sceneIndicatorLights[0] = sceneColor
            self.sceneIndicatorLights[1] = LightValueRGB.GREEN if self.lidClosedMag.value else LightValueRGB.BLACK
            self.sceneIndicatorLights[2] = LightValueRGB.GREEN if self.lidOpenMag.value else LightValueRGB.BLACK
            self.sceneIndicatorLights[3] = LightValueRGB.GREEN if self.leftRimTouch.value else LightValueRGB.BLACK
            self.sceneIndicatorLights[4] = LightValueRGB.GREEN if self.centerRimTouch.value else LightValueRGB.BLACK
            self.sceneIndicatorLights[5] = LightValueRGB.GREEN if self.rightRimTouch.value else LightValueRGB.BLACK
            self.sceneIndicatorLights[6] = LightValueRGB.GREEN if self.bottomTouch.value else LightValueRGB.BLACK

            self.pixels.refresh()
            self.pixels2.refresh()
            if self.enableStatsPrint:
                print( f"{main.latestContext.updateIndex}@{main.when:.3f}  openRatio={openRatio} for {self.lidDrive.lastSetAngle}, sceneColor = {sceneColor} for {self.main.scenes.currentScene}" )

        @fireOnTrue( rising( self.rightRimTouch == True ) )
        def toggleStatsPrint(**kwargs):
            self.enableStatsPrint = not self.enableStatsPrint 
            print( f"self.enableStatsPrint = {self.enableStatsPrint}")
            
        pt = PeriodicTimer( 0.1, manager=main.timers, name="updateStuff" )
        pt.addAction( updateStuff )
        pt.start()
        #main.addTask( updateStuff )

        main.scenes.enableDbgOut = True
      
        print(f"sources = {sceneClosed.sources()}" )


    
    def setupDisplay(self):
        display = self.main.i2cFactory.addDisplayIO_SSD1306(displayHeight=64)
        self.display = display
        display.addBitmap( "/assets/bitmap/TTLogo32.bmp" )
        displayMidHeight = display.displayHeight // 2 - 1
        self.statField = display.addText( "---", x=35, y=displayMidHeight )
        self.potField = display.addText( "---", x=35, y=displayMidHeight + 12 )
        
def demoMain(*args,**kwds):
    
    demo = TreasureChest( *args, **kwds )
    demo.run()