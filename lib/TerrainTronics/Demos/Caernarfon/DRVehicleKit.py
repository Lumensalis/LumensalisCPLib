from LumensalisCP.Simple import *  # http://lumensalis.com/ql/h2Start
#############################################################################
sayAtStartup("start project")  # http://lumensalis.com/ql/h2Main

main = ProjectManager("DRVehicleKit", useWifi=True, autoreload=False)
manualControl = main.addScene()

# add devices
caernarfon = main.TerrainTronics.addCaernarfon()

leftFrontMotor = main.raw.dcMotor( board.IO1, board.IO3 )
leftRearMotor = main.raw.dcMotor( board.IO5, board.IO6 )
rightRearMotor = main.raw.dcMotor( board.IO7, board.IO8 )
rightFrontMotor = main.raw.dcMotor( board.IO37, board.IO33 )
#motorD = main.raw.dcMotor( board.IO9, board.IO14 )

leftFrontMotor.minSpeed = 0.05
leftRearMotor.minSpeed = 0.05
rightRearMotor.minSpeed = 0.05
rightFrontMotor.minSpeed = 0.05
leftFrontMotor.enableDbgOut = True

ui = main.panel
leftFrontMotorSpeed = ui.addPlusMinusOne("left front")
leftRearMotorSpeed = ui.addPlusMinusOne("left rear")
rightRearMotorSpeed = ui.addPlusMinusOne("right rear")
rightFrontMotorSpeed = ui.addPlusMinusOne("right front")
manualSpeedControl = ui.addSwitch("enable manual speed control")
joy = ui.addJoystick()

manualControl.addRule(leftFrontMotor.manualSpeed, leftFrontMotorSpeed)
manualControl.addRule(leftRearMotor.manualSpeed, leftRearMotorSpeed)
manualControl.addRule(rightRearMotor.manualSpeed, rightRearMotorSpeed)
manualControl.addRule(rightFrontMotor.manualSpeed, rightFrontMotorSpeed)

manualControl.addRule(leftFrontMotor.manualOverride, manualSpeedControl)
manualControl.addRule(leftRearMotor.manualOverride, manualSpeedControl)
manualControl.addRule(rightRearMotor.manualOverride, manualSpeedControl)
manualControl.addRule(rightFrontMotor.manualOverride, manualSpeedControl)

main.launchProject(globals())
