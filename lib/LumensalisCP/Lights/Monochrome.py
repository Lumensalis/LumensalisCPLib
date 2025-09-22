from __future__ import annotations

from LumensalisCP.Lights._common import *

#############################################################################

class MonoPattern( Pattern ):
    """ A monochrome pattern.
    """
    def __init__(self,
                 target:LightGroup,
                 **kwargs:Unpack[Pattern.KWDS]
            ):

        super().__init__(target, **kwargs)


    def patternRefresh( self, context:EvaluationContext ) -> None:
        raise NotImplementedError()


#############################################################################

#############################################################################

# __all__ = ['Rainbow','Gauge','Blink','Random','Cylon2','Cylon','prepRGBValue']