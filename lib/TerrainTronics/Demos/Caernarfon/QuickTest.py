from LumensalisCP.ImportProfiler import  getImportProfiler, ImportProfiler
#getImportProfiler.SHOW_IMPORTS = True


#############################################################################
from LumensalisCP.Main.Manager import MainManager

# ImportProfiler.dumpWorstImports(20)


#############################################################################

# ALWAYS START WITH "from LumensalisCP.Simple import *"
from LumensalisCP.Simple import * # http://lumensalis.com/ql/h2Start

#############################################################################
printElapsed( "finished from LumensalisCP.Simple import *" )
ImportProfiler.dumpWorstImports(10)

#############################################################################

sayAtStartup( "start project" ) #  http://lumensalis.com/ql/h2Main


main = ProjectManager(
        profile=True,
        #  profileMemory=3
        #useWifi = False,
    ) 

# setup three different scenes : http://lumensalis.com/ql/h2Scenes
actOne= main.addScene( ) 

# setup Control Inputs : http://lumensalis.com/ql/h2Controller
controlTen = main.panel.addSeconds( startingValue=3.1, min=0.1, max=10.0 )

#############################################################################
# HARDWARE : http://lumensalis.com/ql/h2Hardware
# setup the Caernarfon Castle : http://lumensalis.com/ql/h2Caernarfon
caernarfon = main.TerrainTronics.addCaernarfon( )

neoPixA = caernarfon.addNeoPixels(pixelCount=45) 
# setup neoPixel modules : http://lumensalis.com/ql/h2NeoPixels
firstTwoOnPixA          = neoPixA.nextNLights(2)
leftStoneLights         = neoPixA.ring(3)
centerStoneLights       = neoPixA.ring(7)
rightStoneLights        = neoPixA.ring(3)
frontLidStrip           = neoPixA.stick(8)

# StemmaQT modules

#main.panel.monitor( lightSensor )

#############################################################################
sayAtStartup( "setup touch inputs" ) # http://lumensalis.com/ql/h2Touch
#capTouch = main.adafruitFactory.addMPR121()
#leftStoneTouch, centerStoneTouch, rightStoneTouch= capTouch.addInputs( 1, 2, 4 )
#leftRimTouch, centerRimTouch, rightRimTouch= capTouch.addInputs( 5, 6, 7 )
#bottomTouch = capTouch.addInput( 8 )



#############################################################################
sayAtStartup( "setup oscillators" ) # http://lumensalis.com/ql/h2Oscillators
oscillator2 = Oscillator.Oscillator( low = 0.3, high = 2, frequency = 0.1 )
oscillator = Oscillator.Oscillator(  low = 0, high = 10, frequency = oscillator2 )

#############################################################################
if False:
    sayAtStartup( "setup synth" )

    audio = main.addI2SAudio(
        word_select=board.IO14,     # MAX98357 lrc:green
        bit_clock=board.IO13,       # MAX98357 bclk:yellow
        data=board.IO10,            # MAX98357 din:orange
    )

    testEffect = audio.effects.makeEffect() # filterMode=BAND_PASS)
    testEffect.enableDbgOut = True

    def updateTestEffect(source:Any=None, context:Optional[EvaluationContext]=None) -> None:
        #testEffect.filter.frequency = oscillator.value * 2000 + 100
        v = oscillator.latestValue /10
        testEffect.note.bend = v
        #testEffect.infoOut( "bending to %r", v )

    oscillator.onChange( updateTestEffect  )

    @addPeriodicTaskDef( interval=0.03, name="updateOscillator" )
    def updateOscillator(context:EvaluationContext) -> None:
        oscillator.updateValue(context)

    def touchNote(context:Optional[EvaluationContext]=None, a2:Optional[Any]=None, a3:Optional[Any]=None) -> Any:
        print( "in touchNote" )
        if testEffect.playing:
            print( "releasing note" )
            testEffect.stop()
        else:
            print( "startNote" )
            testEffect.start()

        return 42

    print( f"touchNote = {touchNote}" )

    # fireOnRising( leftRimTouch, do( touchNote ) )
    dot = do( touchNote )
    dot.enableDbgOut = True
    #dot.name = "dot"

    fireDot = fireOnRising( leftRimTouch, dot )
    fireDot.enableDbgOut = True
    leftRimTouch.enableDbgOut = True

#main.panel.monitor( leftRimTouch )

#############################################################################


#############################################################################
# setup LED patterns : http://lumensalis.com/ql/h2Patterns
sayAtStartup( "setup patterns" )

frontLidBlink = PatternTemplate( Blink, frontLidStrip, onTime=0.25, offTime=0.25 )

frontLidStripPattern = Cylon2(frontLidStrip,sweepTime=0.5, dimRatio=0.9, onValue=Colors.RED )
centerPattern = ABFade( centerStoneLights, value=oscillator/20, a =Colors.RED, b=Colors.BLUE )
#rainbowLeft = Rainbow(leftStoneLights,colorCycle=rbCycle, spread=rbs )
rainbowRight = Rainbow(rightStoneLights,colorCycle=1.1, spread=2.0 )
#aglSpinner = Spinner(angleGaugeLights, onValue=Colors.RED, tail=0.42,period=0.49)

lsZ21 = Z21Adapted( controlTen )
csWheel = ColorWheelZ1( lsZ21 )
main.panel.monitor( csWheel, description="Color Wheel based on light sensor" )
#csWheel.enableDbgOut = True

centerSpin = Spinner(centerStoneLights)

actOne.addPatterns( centerSpin)

#############################################################################
# Wrap up and launch : http://lumensalis.com/ql/h2Launch
sayAtStartup( "launch ..." )
main.launchProject( globals() )
