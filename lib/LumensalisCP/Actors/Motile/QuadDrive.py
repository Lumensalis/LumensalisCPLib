from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler

__profileImport = getImportProfiler( __name__, globals() ) 

from LumensalisCP.Actors.Motile.Motile import *

#############################################################################

class BilateralDrive(Motile):
    """ Motile classes which move and steer based on varying speed of the left and right drive systems """
    def __init__(self, **kwds:Unpack[Motile.KWDS]):
        
        super().__init__( **kwds )
        self.__EStopped = False
    
    @notifyingPlusMinusOneOutputProperty(0.0)
    def leftSpeed(self, value:PlusMinusOne, context:EvaluationContext ) -> None:
        #assert isinstance(value, PlusMinusOne), f"manualSpeed must be a PlusMinusOne, not {type(value)}"
        self.__updateSpeed(context)

    @notifyingPlusMinusOneOutputProperty(0.0)
    def rightSpeed(self, value:PlusMinusOne, context:EvaluationContext ) -> None:
        #assert isinstance(value, PlusMinusOne), f"manualSpeed must be a PlusMinusOne, not {type(value)}"
        self.__updateSpeed(context)

    def ESTOP( self, context:Optional[EvaluationContext]=None) -> None:
        self.__EStopped = True
        self.__updateSpeed(UpdateContext.fetchCurrentContext(context))

    def RESET_ESTOP( self, context:Optional[EvaluationContext]=None) -> None:
        """ cancel emergency stop, allow motion to resume"""
        self.__EStopped = False
        self.__updateSpeed(UpdateContext.fetchCurrentContext(context))

    def stop(self, context:Optional[EvaluationContext]=None) -> Behavior:
        raise NotImplementedError("stop method must be implemented in subclass")

    @tunableZeroToOne(1.0)
    def maxForwardSpeed(self, setting: ZeroToOneSetting, context:EvaluationContext ) -> None:
        if self.enableDbgOut: self.dbgOut("maxForwardSpeed changed to %s", setting.value)
        return
    @tunableZeroToOne(1.0)
    def maxReverseSpeed(self, setting: ZeroToOneSetting, context:EvaluationContext ) -> None:
        if self.enableDbgOut: self.dbgOut("maxReverseSpeed changed to %s", setting.value)
        return

    @tunableFloat(1.0)
    def speedScale(self, setting: float, context:EvaluationContext ) -> None:
        if self.enableDbgOut: self.dbgOut("speedScale changed to %s", setting)
        return

    def __cappedSpeed( self, speed:PlusMinusOne, context:Optional[EvaluationContext]=None ) -> PlusMinusOne:
        scaledSpeed = speed * self.speedScale.value
        if scaledSpeed >= 0:
            return min(scaledSpeed, self.maxForwardSpeed.value)
        else:
            return max(scaledSpeed, -self.maxReverseSpeed.value)
        
    def __updateSpeed(self, context:Optional[EvaluationContext]=None) -> None:
        if self.__EStopped:
            self.derivedUpdateSpeed(0.0,0.0,context)
        else:
            left = self.__cappedSpeed(self.leftSpeed.getValue(context), context)
            right = self.__cappedSpeed(self.rightSpeed.getValue(context), context)
            self.derivedUpdateSpeed(left, right, context)

    def derivedUpdateSpeed(self, left:PlusMinusOne, right:PlusMinusOne, context:Optional[EvaluationContext]=None) -> None:
        """ update the speed of the actor based on the current state """
        raise NotImplementedError("derivedUpdateSpeed method must be implemented in subclass")

#############################################################################

__profileImport.complete()