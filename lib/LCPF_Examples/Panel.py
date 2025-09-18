from LumensalisCP.Simple import *  # http://lumensalis.com/ql/h2Start

#############################################################################
main = ProjectManager("PanelsDemo",useWifi=True)


# setup two different scenes : http://lumensalis.com/ql/h2Scenes
shortScene = main.addScene()
tallScene = main.addScene()

# create a shortcut to the "root" panel
demoPanel = main.panel
# add a distance and on/off control to the panel
baseHeight = demoPanel.addMillimeters(100.0, min=10.0, max=1000.0)
onOff = demoPanel.addSwitch()

# add an output to the panel
height = demoPanel.addFloatOutput()
demoPanel.monitor( height )

# set value of result is based on scene
shortScene.addRule( height, baseHeight / 2)
tallScene.addRule( height, baseHeight * 2 )

main.launchProject(globals())
