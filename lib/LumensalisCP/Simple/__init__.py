""" common imports for simple (typically single file, no class) projects

Intended to be used as `from LumensalisCP.Simple import *`
"""

import rainbowio

from LumensalisCP.Demo.DemoCommon import *
from LumensalisCP.Lights.RGB import *
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Triggers.Fireable import Fireable
from LumensalisCP.Main.PreMainConfig import *

def ProjectManager( ) -> MainManager:
    return  MainManager.initOrGetManager()

def getColor( v:AnyRGBValue ) -> RGB:
    """ convert __v__ to an RGB value

    :param v: value to be converted
    :type v: AnyRGBValue
    :return: _description_
    :rtype: RGB
    """
    return RGB.toRGB(v)

def do( cb, *args, **kwds ):
    return Fireable.makeCallback( cb, *args, **kwds )

def doDbg( cb, *args, **kwds ):
    return Fireable.makeDbgCallback( cb, *args, **kwds )

class ColorSource(InputSource):
    #def __init__( self, name:Optional[str]=None ):
    
    def getColor(self, context:EvaluationContext ) -> RGB:
        raise NotImplementedError
    
    def getDerivedValue(self, context:EvaluationContext) -> RGB:
        return self.getColor(context)


class ColorWheel(ColorSource):
    def __init__( self, spin:Evaluatable, **kwargs ):
        super().__init__(**kwargs)
        self.spin = spin

    def getColor(self, context:EvaluationContext ) -> RGB:
        spinValue = context.valueOf( self.spin )
        wheelValue = rainbowio.colorwheel( spinValue )
        rv = RGB.fromNeoPixelRGBInt( wheelValue )
        if self.enableDbgOut:  self.dbgOut( 'getColor rv=%r,  spin=%r, wheel=%X', rv, spinValue, wheelValue )
        return rv

class PipeInputSource(InputSource):
    def __init__( self, inputSource:Evaluatable, **kwargs ):
        super().__init__(**kwargs)
        self.inputSource = inputSource
        
    def getPipedValue(self, context:EvaluationContext, v:Any ) -> Any:
        raise NotImplementedError
    
    def getDerivedValue(self, context:EvaluationContext) -> RGB:
        v = context.valueOf(self.inputSource)
        return self.getPipedValue(context,v)

class Z21Adapted(PipeInputSource):
    def __init__( self, inputSource:Evaluatable, min:Optional[Any]=None, max_value:Optional[Any]=None, **kwargs ): # pylint: disable=redefined-builtin
        super().__init__(inputSource,**kwargs)
        self._min = min
        self._max = max_value
        self._span = None if min is None or max_value is None else max_value - min
        
        
    def getPipedValue(self, context:EvaluationContext, v:Any ) -> Any:
        if self._span is None:
            self._min = v
            self._max = v
            self._span = 0
        elif v < self._min:
            self._min = v
            self._span = self._max - self._min
        elif v > self._max:
            self._max = v
            self._span = self._max - self._min
        
        if self._span == 0: return 0
        return (v - self._min) / self._span
