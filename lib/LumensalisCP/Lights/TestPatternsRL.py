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

cgSteps = 256
copperGradient = fancy.expand_gradient([
        (0.0, 0x97461A),
        (0.2, 0x3C1E06),
        (0.3, 0xFBD8C5),
        (0.83, 0x6C2E16),
        (0.92, 0xEFDBCD),
        (1.0, 0x97461A),
    ],
    cgSteps   # Number of steps
)

#############################################################################

def TestPattern1_reset( self:TestPattern1,  context:Optional[EvaluationContext]=None  ) -> None:
    self._color = RGB(0,0,0)
    self.setRefreshRate( UpdateContext.fetchCurrentContext(context), 0.02 )

def TestPattern1_refresh( self:TestPattern1, context:EvaluationContext ) -> None:

    iMod = cgSteps / 4
    i = context.updateIndex % iMod / (iMod-1)
    fcolor = fancy.palette_lookup( copperGradient, i ).pack()

    target = self.target
    color = self._color
    color.setFromNeoPixelRGBInt( fcolor )
    color.brightness =  0.5 
    if self.enableDbgOut: # or True:
        self.infoOut( "refresh i=%.2f idx=%d color=%r" % (i, context.updateIndex, color) )
    for px in range(target.lightCount):
        target[px] = color

#############################################################################


def TestPattern2_reset( self:TestPattern2,  context:Optional[EvaluationContext]=None  ) -> None:
    self._colors = [RGB(0,0,0) for _ in range(self.target.lightCount)]
    self.setRefreshRate( UpdateContext.fetchCurrentContext(context), 0.02 )

def TestPattern2_refresh( self:TestPattern2, context:EvaluationContext ) -> None:
    target = self.target

    for px in range(self.target.lightCount):
        color = self._colors[px]
        color.r = randomZeroToOne()
        color.g = randomZeroToOne()
        color.b = randomZeroToOne()
        color.brightness =  0.5
        
        target[px] = color

#############################################################################

engineSideGradientSteps = 64

engineSideGradient = fancy.expand_gradient([
        (0.0, 0xFF0000),
        (0.1, 0x800000),
        (0.2, 0xCC0000),
        (0.3, 0xA00000),
        (0.4, 0x600000),
        (0.5, 0x800000),
        (0.6, 0x200000),
        (0.7, 0x400000),
        (1.0, 0x000000),
    ],
    engineSideGradientSteps   # Number of steps
)


def TestPattern3_reset( self:TestPattern3,  context:Optional[EvaluationContext]=None  ) -> None:
    self._colors = [RGB(0,0,0) for _ in range(self.target.lightCount)]
    self.setRefreshRate( UpdateContext.fetchCurrentContext(context), 0.02 )

def TestPattern3_refresh( self:TestPattern3, context:EvaluationContext ) -> None:

    cycleMs = 733

    i = int( context.newNow * 1000) % cycleMs

    fcolor = fancy.palette_lookup( copperGradient, i/cycleMs ).pack()

    target = self.target
    for px in range(target.lightCount):
        color = self._colors[px]
        color.setFromNeoPixelRGBInt( fcolor )
        
        target[px] = color
pass

#############################################################################

from LumensalisCP.Lights.TestPatterns import PatternRLTestBase

print( f"resetting {len(PatternRLTestBase._reloadablePatterns)} reloadable patterns" ) # pyright: ignore[reportPrivateUsage]
for __pattern in PatternRLTestBase._reloadablePatterns: # pyright: ignore[reportPrivateUsage]
    __pattern.reset()

#############################################################################