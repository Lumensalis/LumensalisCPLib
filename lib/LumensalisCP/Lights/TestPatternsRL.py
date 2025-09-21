#############################################################################


# pylint: disable=unused-import,import-error,reimported,import-outside-toplevel
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

from LumensalisCP.Lights.Light import *
from LumensalisCP.IOContext import *
#from LumensalisCP.Main.Expressions import NamedOutputTarget, EvaluationContext
from LumensalisCP.Lights.Pattern import *
from random import random as randomZeroToOne, randint

import adafruit_fancyled.adafruit_fancyled as fancy
from LumensalisCP.Lights.RGB import RGB

import asyncio

if TYPE_CHECKING:
    from LumensalisCP.Lights.TestPatterns import TestPattern1, TestPattern2, TestPattern3

#############################################################################

cgSteps = 256

class RGBGradient:
    def __init__(self, gradient:list[fancy.CRGB]) -> None:
        self.values:list[RGB] = []
        for v in gradient:
            if isinstance(v, int):
                self.values.append(RGB.fromNeoPixelRGBInt(v))
            else:
                assert isinstance(v, fancy.CRGB), f"Expected fancy.CRGB, got {type(v)} [{len(self.values)}]"
                self.values.append(v.pack())
        

    def getInto(self, out:RGB, position:float) -> None:
        position = max(0.0, min(1, position) )
        index = int(position * (len(self.values)-1))
        out.setFrom( self.values[index] )

_copperFancy = fancy.expand_gradient([
        (0.0, 0x97461A),
        (0.2, 0x3C1E06),
        (0.3, 0xFBD8C5),
        (0.83, 0x6C2E16),
        (0.92, 0xEFDBCD),
        (1.0, 0x97461A),
    ],
    cgSteps   # Number of steps
)

copperGradient = RGBGradient(_copperFancy )

#############################################################################

def TestPattern1_reset( self:TestPattern1,  context:Optional[EvaluationContext]=None  ) -> None:
    self._color = RGB(0,0,0)
    self.setRefreshRate( UpdateContext.fetchCurrentContext(context), 0.02 )

def TestPattern1_refresh( self:TestPattern1, context:EvaluationContext ) -> None:

    iMod = cgSteps / 4
    i = context.updateIndex % iMod / (iMod-1)

    target = self.target
    copperGradient.getInto( self._color, i )
    #color.brightness =  0.5 
    if self.enableDbgOut: # or True:
        self.infoOut( "refresh i=%.2f idx=%d color=%r" % (i, context.updateIndex, color) )
    for px in range(target.lightCount):
        target[px] = self._color
        #break

#############################################################################


def TestPattern2_reset( self:TestPattern2,  context:Optional[EvaluationContext]=None  ) -> None:
    self._colors = [RGB(0,0,0) for _ in range(self.target.lightCount)]
    self._randomCount = 30
    self._randomColors = [
        RGB(
            randomZeroToOne(),
            randomZeroToOne(),
            randomZeroToOne()) for _ in range(self._randomCount)
        ]
    self.setRefreshRate( UpdateContext.fetchCurrentContext(context), 0.02 )

def TestPattern2_refresh( self:TestPattern2, context:EvaluationContext ) -> None:
    if getattr(self, '_randomCount', None) is None:
        TestPattern2_reset( self, context )
        
    target = self.target

   # r = 
    for px in range(self.target.lightCount):
        r = randint(0,self._randomCount-1)
        target[px] = self._randomColors[r]
        #break

#############################################################################

engineSideGradientSteps = 128

engineSideGradient = RGBGradient( fancy.expand_gradient([
        (0.00, 0x000000),
        (0.07, 0x0f3d2f),
        (0.14, 0x8025a5),
        (0.17, 0x3CF07e),
        (0.33, 0xA35500),
        (0.39, 0x6000F0),
        (0.51, 0x38705a),
        (0.63, 0x2f6a3d),
        (0.77, 0x432167),
        (1.00, 0x000000),
    ],
    engineSideGradientSteps   # Number of steps
) )


def TestPattern3_reset( self:TestPattern3,  context:Optional[EvaluationContext]=None  ) -> None:
    self._colors = [RGB(0,0,0) for _ in range(self.target.lightCount)]
    self.setRefreshRate( UpdateContext.fetchCurrentContext(context), 0.02 )

def TestPattern3_refresh( self:TestPattern3, context:EvaluationContext ) -> None:

    cycleMs = 5733

    i = int( context.newNow * 1000) % cycleMs

    #fcolor = fancy.palette_lookup( engineSideGradient, i/cycleMs ).pack()
    color = self._colors[0]
    #color.setFromNeoPixelRGBInt( fcolor )
    engineSideGradient.getInto( color, i/cycleMs )

    await asyncio.sleep(0.2)
    target = self.target
    for px in range(target.lightCount):
        target[px] = color
pass

#############################################################################

from LumensalisCP.Lights.TestPatterns import PatternRLTestBase

print( f"resetting {len(PatternRLTestBase._reloadablePatterns)} reloadable patterns" ) # pyright: ignore[reportPrivateUsage]
for __pattern in PatternRLTestBase._reloadablePatterns: # pyright: ignore[reportPrivateUsage]
    __pattern.reset()

#############################################################################