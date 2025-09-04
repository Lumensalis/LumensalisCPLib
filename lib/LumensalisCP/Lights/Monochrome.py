from __future__ import annotations

from LumensalisCP.Lights._common import *

#############################################################################

class MonoPatterrn( Pattern ):
    """ A monochrome pattern.
    """
    def __init__(self,
                 target:LightGroup,
                 **kwargs:Unpack[Pattern.KWDS]
            ):

        super().__init__(target, **kwargs)


    def refresh( self, context:EvaluationContext ):
        when = self.offsetWhen( context )
        self.__latestCycleWhen = when
        cc = max(0.001,context.valueOf(self.colorCycle))
        self.__latestCycleValue = cc
        #print( f"cc = {cc} from {self.colorCycle}")
        A = (when + self.__colorCycleWhenOffset) / cc
        ensure( type(A) is float, f"A is {type(A)}, not float" )
        
        target = self.target
        spread = context.valueOf(self.spread)
        if spread == 0:
            pxStep = 0
        else:
            pxStep = 1 / (target.lightCount * context.valueOf(spread) )
            
        # set each pixel
        for px in range(target.lightCount):
            target[px] = wheel1( A + (px * pxStep) )

#############################################################################

#############################################################################

# __all__ = ['Rainbow','Gauge','Blink','Random','Cylon2','Cylon','prepRGBValue']