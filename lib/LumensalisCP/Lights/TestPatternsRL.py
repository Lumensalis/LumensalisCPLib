#############################################################################


# pylint: disable=unused-import,import-error,reimported,import-outside-toplevel
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

from LumensalisCP.Lights.Light import *
from LumensalisCP.IOContext import *
#from LumensalisCP.Main.Expressions import NamedOutputTarget, EvaluationContext
from LumensalisCP.Lights.Pattern import *
from random import random as randomZeroToOne, randint

import adafruit_fancyled.adafruit_fancyled as fancy

if TYPE_CHECKING:
    from LumensalisCP.Lights.TestPatterns import TestPattern1, TestPattern2, TestPattern3

#############################################################################

copperGradient = fancy.expand_gradient([
        (0.0, 0x97461A),
        (0.3, 0xFBD8C5),
        (0.83, 0x6C2E16),
        (1.0, 0xEFDBCD)
    ],
    256  # Number of steps
)

def TestPattern1_reset( self:TestPattern1,  context:Optional[EvaluationContext]=None  ) -> None:
    pass

def TestPattern1_refresh( self:TestPattern1, context:EvaluationContext ) -> None:
    pass

#############################################################################

def TestPattern2_reset( self:TestPattern2,  context:Optional[EvaluationContext]=None  ) -> None:
    pass

def TestPattern2_refresh( self:TestPattern2, context:EvaluationContext ) -> None:
    pass

#############################################################################

def TestPattern3_reset( self:TestPattern3,  context:Optional[EvaluationContext]=None  ) -> None:
    pass

def TestPattern3_refresh( self:TestPattern3, context:EvaluationContext ) -> None:
    pass

#############################################################################

