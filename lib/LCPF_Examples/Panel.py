from LumensalisCP.ImportProfiler import ImportProfiler
ImportProfiler.SHOW_IMPORTS = True

from LumensalisCP.Simple import *  # http://lumensalis.com/ql/h2Start
#############################################################################
main = ProjectManager("PanelsDemo")

scene1 = main.addScene()
scene2 = main.addScene()

demoPanel = main.panel

distance = demoPanel.addMillimeters(100.0, min=10.0, max=1000.0)
onOff = demoPanel.addSwitch()



result = demoPanel.addFloatOutput()

demoPanel.monitor( result )
scene1.addRule( result, distance )
scene2.addRule( result, distance / 2 )

main.launchProject(globals())
