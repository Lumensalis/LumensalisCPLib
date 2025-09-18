from LumensalisCP.Simple import *  # http://lumensalis.com/ql/h2Start
#############################################################################

from LumensalisCP.Actors.Motile.SkidSteer import SkidSteerDCMotor
from LumensalisCP.Lights.TestPatterns import *
from LumensalisCP.pyCp.importlib import reload
from . import DRVehicleKitRL

main = ProjectManager("DRVehicleKit", useWifi=True, autoreload=False)
manualControl = main.addScene()

# add devices
caernarfon = main.TerrainTronics.addCaernarfon()
neoPixels = caernarfon.addNeoPixels(pixelCount=30) 

carPixel = neoPixels.nextNLights(1)
tri = neoPixels.ring(3)

eRingFront = neoPixels.ring(8)
eInnerStrip = neoPixels.stick(8)
eRingRear = neoPixels.ring(8)

drive = SkidSteerDCMotor( main=main,
    motorPins = [board.IO1, board.IO3, board.IO6, board.IO5,
                  board.IO7, board.IO8, board.IO9, board.IO14
    ] )
drive.speedScale = 0.77

nunchuk = caernarfon.adafruitFactory.addNunchuk( )

def reloadStuff(context:Optional[EvaluationContext]=None) -> None:
    print( f"reloading ")
    DRVehicleKitRL.preReload( context )
    reload( DRVehicleKitRL )
    
ui = main.panel
#joy = ui.addJoystick()

ui.monitorPlusMinusOne( nunchuk.joystick.x )
ui.monitorPlusMinusOne( nunchuk.joystick.y )

ui.monitorFloat( nunchuk.accel.ax )
ui.monitorFloat( nunchuk.accel.ay )
ui.monitorFloat( nunchuk.accel.az )

ui.monitor( nunchuk.buttons.c )
ui.monitor( nunchuk.buttons.z )

#leftPortion = Z21Adapted( (joy.x + 1)/2) 
#rightPortion = Z21Adapted( 1 - leftPortion ) #(joy.x *-1 + 1) / 2) 

#leftSpeed = PipeInputSource( joy.y * leftPortion )
#rightSpeed = PipeInputSource( joy.y * rightPortion)
#leftSpeed = PipeInputSource( joy.y )
#rightSpeed = PipeInputSource( joy.x )

rbColorCycle = Z21Adapted( nunchuk.accel.ax )
rbSpread = Z21Adapted( nunchuk.accel.ay )
#ui.monitorPlusMinusOne( leftSpeed )
#ui.monitorPlusMinusOne( rightSpeed )
manualControl.addPatterns(
    Rainbow(tri,
                 colorCycle = rbColorCycle* 3 + 0.3,
                 spread = rbSpread * 4 + 0.3,
                 ),
    TestPattern1(eRingFront),
    TestPattern2(eInnerStrip),
    TestPattern3(eRingRear),
)
                 

manualControl.addRule(drive.leftSpeed, nunchuk.joystick.x )
manualControl.addRule(drive.rightSpeed, nunchuk.joystick.y )


main.launchProject(globals())
