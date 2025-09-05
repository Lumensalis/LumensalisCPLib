from LumensalisCP.Simple import *  # http://lumensalis.com/ql/h2Start
#############################################################################
sayAtStartup("start project")  # http://lumensalis.com/ql/h2Main
from LumensalisCP.Actors.Motile.SkidSteer import SkidSteerDCMotor
main = ProjectManager("DRVehicleKit", useWifi=True, autoreload=False)
manualControl = main.addScene()

# add devices
caernarfon = main.TerrainTronics.addCaernarfon()

drive = SkidSteerDCMotor( main=main,
    motorPins = [board.IO1, board.IO3, board.IO6, board.IO5,
                  board.IO7, board.IO8, board.IO37, board.IO38
    ] )
drive.speedScale = 0.35

if False:
    drive.leftFront.enableDbgOut = True
    drive.leftFront.inA.enableDbgOut = True
    drive.leftFront.inB.enableDbgOut = True
    drive.leftSpeed.enableDbgOut = True

ui = main.panel
joy = ui.addJoystick()

#leftPortion = Z21Adapted( (joy.x + 1)/2) 
#rightPortion = Z21Adapted( 1 - leftPortion ) #(joy.x *-1 + 1) / 2) 

#leftSpeed = PipeInputSource( joy.y * leftPortion )
#rightSpeed = PipeInputSource( joy.y * rightPortion)
leftSpeed = PipeInputSource( joy.y )
rightSpeed = PipeInputSource( joy.x )

#ui.monitorPlusMinusOne( leftSpeed )
#ui.monitorPlusMinusOne( rightSpeed )

manualControl.addRule(drive.leftSpeed, leftSpeed)
manualControl.addRule(drive.rightSpeed, rightSpeed)


main.launchProject(globals())
