from LumensalisCP.Main.PreMainConfig import sayAtStartup, printElapsed, pmc_gcManager
from LumensalisCP.ImportProfiler import ImportProfiler
ImportProfiler.SHOW_IMPORTS = False

# pyright: reportUnusedImport=false, reportUnusedVariable=false
#############################################################################

# ALWAYS START WITH "from LumensalisCP.Simple import *"
#from LumensalisCP.Simple import * # http://lumensalis.com/ql/h2Start
from LumensalisCP.Main.ProjectManager import ProjectManager
from LumensalisCP.Main.Helpers import *
from LumensalisCP.common import * # http://lumensalis.com/ql/h2Start

from LumensalisCP.Temporal import Oscillator
from LumensalisCP.Lights.Patterns import Gauge
from LumensalisCP.Triggers.Fire import fireOnRising

# from LumensalisCP.Audio import Audio
import board

#############################################################################
printElapsed( "finished from LumensalisCP.Simple import *" )
ImportProfiler.dumpWorstImports(10)

#############################################################################

sayAtStartup( "start project" ) #  http://lumensalis.com/ql/h2Main
main = ProjectManager(
        #profile=True,
        #  profileMemory=3
        #useWifi = False,
    ) 

actOne= main.addScene( ) # http://lumensalis.com/ql/h2Scenes

# setup Control Inputs : http://lumensalis.com/ql/h2Controller
controlTen = main.panel.addSeconds( startingValue=3.1, min=0.1, max=10.0 )

#############################################################################
# HARDWARE : http://lumensalis.com/ql/h2Hardware
# setup the Caernarfon Castle : http://lumensalis.com/ql/h2Caernarfon
caernarfon = main.TerrainTronics.addCaernarfon( )

sayAtStartup( "setup synth" )
audio = main.addI2SAudio(
    word_select=board.IO14,     # MAX98357 lrc:green
    bit_clock=board.IO13,       # MAX98357 bclk:yellow
    data=board.IO10,            # MAX98357 din:orange
)

neoPixA = caernarfon.addNeoPixels(pixelCount=45) 
# setup neoPixel modules : http://lumensalis.com/ql/h2NeoPixels
firstTwoOnPixA          = neoPixA.nextNLights(2)
leftStoneLights         = neoPixA.ring(3)
centerStoneLights       = neoPixA.ring(7)
rightStoneLights        = neoPixA.ring(3)
frontLidStrip           = neoPixA.stick(8)
neoPixB = caernarfon.addNeoPixels(servoPin=3,pixelCount=35)
sceneIndicatorLights    = neoPixB.stick(8)
angleGaugeLights        = neoPixB.ring(12)

# StemmaQT modules
# main.panel.monitor( lightSensor )

#############################################################################

sayAtStartup( "setup interconnected oscillators" )
oscillator2 = Oscillator.Oscillator( frequency = 0.1, low = 0.3, high = 2 )
oscillator = Oscillator.Oscillator(  frequency = oscillator2, low = 0, high = 10 )
# oscillator will range from 0 to 10 with a frequency from  from 0.3 to 2 HZ
oscillator.activate() 

sayAtStartup( "setup sound effect" )
testEffect = audio.effects.makeEffect( filterMode="NOTCH", wave='square' )
testEffect.amplitude = 0.5 + Z21Adapted(oscillator2) * 0.5
testEffect.bend = oscillator / 10.0
testEffect.filterFrequency = (oscillator*oscillator2) * 500 + 100 

sayAtStartup( "setup LED ring" ) # http://lumensalis.com/ql/h2Touch
wheel = ColorWheelZ1( Z21Adapted(oscillator2) )
gauge = Gauge( angleGaugeLights, value=Z21Adapted(oscillator), onValue=wheel )
actOne.addPatterns( gauge )

sayAtStartup( "setup touch inputs" ) # http://lumensalis.com/ql/h2Touch
capTouch = main.adafruitFactory.addMPR121()
leftRimTouch, centerRimTouch, rightRimTouch= capTouch.addInputs( 5, 6, 7 )

# touching leftRimTouch will turn testEffect on and off
fireOnRising( leftRimTouch, testEffect.toggle )

#############################################################################

#############################################################################
# Wrap up and launch : http://lumensalis.com/ql/h2Launch
sayAtStartup( "launch ..." )
ImportProfiler.dumpWorstImports(10)
main.launchProject( globals() )
