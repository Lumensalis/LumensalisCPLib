from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
__profileImport = getImportProfiler( __name__, globals() ) 

from LumensalisCP.Behaviors._common import *
from LumensalisCP.Behaviors.Actor import Actor
from LumensalisCP.Behaviors.Behavior import Behavior


class Motile(Actor):
    """ base class for mobile actors which can move around """
    def __init__(self, **kwds:Unpack[Actor.KWDS]):
        
        super().__init__( **kwds )

    @notifyingBoolOutputProperty(False)
    def estopInput(self, value:bool, context:EvaluationContext ) -> None:
        if value:
            self.ESTOP(context)

    def ESTOP( self, context:Optional[EvaluationContext]=None) -> None:
        """ emergency stop - cease all motion and keep everything off until RESET_ESTOP """
        raise NotImplementedError("ESTOP method must be implemented in subclass")

    def RESET_ESTOP( self, context:Optional[EvaluationContext]=None) -> None:
        """ cancel emergency stop, allow motion to resume"""
        raise NotImplementedError("ESTOP method must be implemented in subclass")


    def stop(self, context:Optional[EvaluationContext]=None) -> Behavior:
        raise NotImplementedError("stop method must be implemented in subclass")


__profileImport.complete()