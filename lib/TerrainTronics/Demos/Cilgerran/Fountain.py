from LumensalisCP.Simple import *  # http://lumensalis.com/ql/h2Start
#############################################################################
sayAtStartup("start project")  # http://lumensalis.com/ql/h2Main

main = ProjectManager("CilgerranFountain", useWifi=True, autoreload=False)
manualControl = main.addScene()
waterWheel = main.addScene()
shishiOdoshi = main.addScene()

# add devices
cilgerran = main.TerrainTronics.addCilgerran(withMotor=True, ledCount=6)
fountainTurret = cilgerran.motor
fountainTurret.minSpeed = 0.35

cilgerran.ledSource.brightness = 1.0
 # 0/1 reserved for fountain controls
fountainChannels = cilgerran.ledSource.nextNLights(2) 
cilLeds = cilgerran.ledSource.nextNLights(4)
fountainFlow = fountainChannels[0]

# setup tunables
rotateTimeBetweenPositions = main.tunables.addSeconds(2.6)
rotationSpeedBetweenPositions = main.tunables.addZeroToOne(0.9)
shishiOdoshiFlowRate = main.tunables.addZeroToOne(0.5, "shishi-odoshi flow rate")
waterWheelFlowRate = main.tunables.addZeroToOne(0.95, "water wheel flow rate")

# setup panel controls - will be available in the UI
ui = main.panel
ui.displayName = "Fountain"
motorSpeed = ui.addPlusMinusOne("manual turret rotation speed")
manualSpeedControl = ui.addSwitch("enable manual speed control")
ui.monitorFloat( cilgerran.batteryMonitor ).displayName = "Battery Voltage"
ui.monitorString( main.scenes.currentSceneInput ).displayName = "Current Scene"
ui.monitorPlusMinusOne( motorSpeed )

sliders = main.addPanel(displayName="Sliders", useSliders=True)
flowRate = sliders.addZeroToOne(0.7, "fountain flow rate")
main.dmx.addDimmerInputs( 1, "Bamboo Lamp", "Fountain Lamp", "WheelLamp",
                          lights=cilLeds, panel=sliders ) 

jogPanel = main.addPanel(displayName="Jog Controls")
rotateDuration = jogPanel.addSeconds(2.6, "rotation duration", min=0, max=5)
rotateSpeed = jogPanel.addZeroToOne(0.8, "rotation speed")
jogLeft = jogPanel.addTrigger("rotate left", 
        action=do(fountainTurret.spin, rotateSpeed*-1, rotateDuration))
jogRight = jogPanel.addTrigger("rotate right", 
        action=do(fountainTurret.spin, rotateSpeed, rotateDuration))


fountainFlow.enableDbgOut = True
manualControl.addRule(fountainFlow, flowRate)
manualControl.addRule(fountainTurret.manualSpeed, motorSpeed)
manualControl.addRule(fountainTurret.manualOverride, manualSpeedControl)

waterWheel.setOnEnter( fountainFlow, waterWheelFlowRate)
waterWheel.onChangeTo(shishiOdoshi, do(
    fountainTurret.spin, rotationSpeedBetweenPositions, rotateTimeBetweenPositions))

shishiOdoshi.setOnEnter(fountainFlow, shishiOdoshiFlowRate)
shishiOdoshi.onChangeTo(waterWheel, do(
    fountainTurret.spin, rotationSpeedBetweenPositions*-1, rotateTimeBetweenPositions))

main.launchProject(globals())
