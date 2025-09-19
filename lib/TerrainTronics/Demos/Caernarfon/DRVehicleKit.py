from LumensalisCP.Main.PreMainConfig import *

pmc_mainLoopControl.ENABLE_PROFILE = True

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

enginePixels = caernarfon.addNeoPixels(servoPin=1,pixelCount=42) 

carPixel = neoPixels.nextNLights(1)
tri = neoPixels.ring(3)

eRingFront8 = enginePixels.ring(8)
eRingFront3 = enginePixels.ring(3)
eInnerStripA = enginePixels.stick(8)
eInnerStripB = enginePixels.stick(8)
eRingRear8 = enginePixels.ring(8)
eRingRear3 = enginePixels.ring(3)

drive = SkidSteerDCMotor( main=main,
    motorPins = [board.IO1, board.IO3, board.IO6, board.IO5,
                  board.IO7, board.IO8, board.IO9, board.IO14
    ],
     motorKwds= {'lowerLimit':0.1}
      
    )
drive.speedScale = 1.4

nunchuk = caernarfon.adafruitFactory.addNunchuk( refreshRate=0.07)

def reloadStuff(context:Optional[EvaluationContext]=None) -> None:
    print( f"reloading ")
    DRVehicleKitRL.preReload( context )
    reload( DRVehicleKitRL )
    
ui = main.panel
#joy = ui.addJoystick()

if False:
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

#ui.monitorPlusMinusOne( leftSpeed )
#ui.monitorPlusMinusOne( rightSpeed )


#rbColorCycle = Z21Adapted( nunchuk.accel.ax )
#rbSpread = Z21Adapted( nunchuk.accel.ay )

manualControl.addPatterns(
    #Rainbow(tri, colorCycle = 4, spread=0.7
                 #colorCycle = rbColorCycle* 3 + 0.3,
                 #spread = rbSpread * 4 + 0.3,
    #             ),
    TestPattern1(eRingFront3),
    TestPattern2(eRingFront8),
    TestPattern3(eInnerStripA),
    #TestPattern3(eInnerStripB),
    #TestPattern2(eRingRear8),
    #TestPattern1(eRingRear3),
)
                 

#manualControl.addRule(drive.leftSpeed, nunchuk.joystick.x )
#manualControl.addRule(drive.rightSpeed, nunchuk.joystick.y )


manualControl.setRefreshRate(getCurrentEvaluationContext(), 0.01)

main.launchProject(globals())
