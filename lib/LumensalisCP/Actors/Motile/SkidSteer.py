from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__profileImport = getImportProfiler( __name__, globals() ) 

from LumensalisCP.Actors.Motile.QuadDrive import *
from LumensalisCP.Tunable.Tunables import *
from LumensalisCP.Behaviors.Rotation import DCMotorSpinner
import microcontroller

#############################################################################

class SkidSteerDCMotor(BilateralDrive):
    """ Motile classes which move and steer based on varying speed of the left and right drive systems """
    class KWDS(BilateralDrive.KWDS):
        motorPins:NotRequired[list[microcontroller.Pin]]
        motors:NotRequired[list[DCMotorSpinner]]

    def __init__(self, motors:Optional[list[DCMotorSpinner]]=None, 
                 motorPins:Optional[list[microcontroller.Pin]]=None,
                   **kwds:Unpack[Motile.KWDS]
            ) -> None:

        super().__init__( **kwds )
        if motors is not None:
            assert motorPins is None, "Cannot specify both motors and motorPins"
        else:
            assert motorPins is not None, "Must specify either motors or motorPins"
            assert len(motorPins) == 8, "Must specify exactly 8 motorPins"
            assert all(isinstance(p, microcontroller.Pin) for p in motorPins), "All motorPins must be microcontroller.Pin instances"
            
            main = self.main
            assert main is not None
            motorKwds = {}
            motors = [
                main.raw.dcMotor( motorPins[0], motorPins[1], **motorKwds ),
                main.raw.dcMotor( motorPins[2], motorPins[3], **motorKwds ),
                main.raw.dcMotor( motorPins[4], motorPins[5], **motorKwds ),
                main.raw.dcMotor( motorPins[6], motorPins[7], **motorKwds ),
            ]

        assert len(motors) == 4, "Must specify exactly 4 motors"
        assert all(isinstance(m, DCMotorSpinner) for m in motors), "All motors must be DCMotorSpinner instances"
        self.motors:NliList[DCMotorSpinner] = NliList("motors")
        context = UpdateContext.fetchCurrentContext(None)
        for motor in motors:
            motor.nliSetContainer(self.motors)
            motor.manualOverride.set(True,context)
        self.leftFront:DCMotorSpinner = motors[0]
        self.leftRear:DCMotorSpinner = motors[1]
        self.rightFront:DCMotorSpinner = motors[2]
        self.rightRear:DCMotorSpinner = motors[3]


    def derivedUpdateSpeed(self, left:PlusMinusOne, right:PlusMinusOne, context:Optional[EvaluationContext]=None) -> None:
        """ update the speed of the actor based on the current state """
        if self.enableDbgOut: self.dbgOut("derivedUpdateSpeed: left=%s right=%s", left, right)
        if context is None: context = UpdateContext.fetchCurrentContext(context)
        self.leftFront.manualSpeed.set( left, context=context )
        self.leftRear.manualSpeed.set( left, context=context )
        self.rightFront.manualSpeed.set( right, context=context )
        self.rightRear.manualSpeed.set( right, context=context )



__profileImport.complete()
