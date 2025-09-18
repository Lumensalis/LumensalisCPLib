from LumensalisCP.ImportProfiler import ImportProfiler
ImportProfiler.SHOW_IMPORTS = True

from LumensalisCP.Simple import *  # http://lumensalis.com/ql/h2Start

#############################################################################
main = ProjectManager("PanelsDemo", autoreload=False)

from LumensalisCP.Main import RawRL
from LumensalisCP.pyCp.importlib import reload

scene1 = main.addScene()
scene2 = main.addScene()

demoPanel = main.panel

distance = demoPanel.addMillimeters(100.0, min=10.0, max=1000.0)
onOff = demoPanel.addSwitch()
result = demoPanel.addFloatOutput()

caernarfon = main.TerrainTronics.addCaernarfon()

ir = caernarfon.addIrRemote(codenames="dvd_remote", 
                            showUnhandled = True,
                            #refreshRate=5.0 
                            )


if False:
    analogIn = main.raw.getAnalogInput(pin=board.IO3)
    demoPanel.monitor( analogIn )

if True:
    servoIn = main.raw.getPWMInput(pin=board.IO13)
    demoPanel.monitor( servoIn )

    demoPanel.monitor( servoIn.readCycles )
    demoPanel.monitor( servoIn.pulsesDetected )

    rl = demoPanel.addTrigger()# action = servoIn.rl )
    boop = demoPanel.addTrigger()# action = servoIn.boop )
    rl.addAction( servoIn.rl )
    boop.addAction( servoIn.boop )


def foo( context:Optional[EvaluationContext]=None ) -> None:
    print( "foo() called" )
    reload(RawRL)

def bar( context:Optional[EvaluationContext]=None ) -> None:
    RawRL.bar( context )

ir.onCode( "DOWN", action=foo ) # sc do( lid.close ).unless( handTooClose ) )
ir.onCode( "UP", action=bar ) # sc do( lid.close ).unless( handTooClose ) )

demoPanel.monitor( result )






# result is based on scene
scene1.addRule( result, distance )
scene2.addRule( result, distance / 2 )

main.launchProject(globals())
