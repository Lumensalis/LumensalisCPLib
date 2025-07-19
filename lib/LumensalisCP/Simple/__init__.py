""" common imports for simple (typically single file, no class) projects

Intended to be used as `from LumensalisCP.Simple import *`
"""

from TerrainTronics.Demos.DemoCommon import *
from LumensalisCP.Lights.Values import RGB
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Triggers.Fireable import Fireable
from LumensalisCP.Main.PreMainConfig import *

def ProjectManager( ) -> MainManager:
    return  MainManager.initOrGetManager()

def getColor( v ) -> RGB:
    return LightValueRGB.toRGB(v)


def do( cb, *args, **kwds ):
    return Fireable.makeCallback( cb, *args, **kwds )

def doDbg( cb, *args, **kwds ):
    return Fireable.makeDbgCallback( cb, *args, **kwds )

class ColorSource(InputSource):
    #def __init__( self, name:Optional[str]=None ):
    
    def getColor(self, context:EvaluationContext ) -> RGB:
        raise NotImplemented
    
    def getDerivedValue(self, context:EvaluationContext) -> RGB:
        return self.getColor(context)

import rainbowio

class ColorWheel(ColorSource):
    def __init__( self, spin:Evaluatable, **kwargs ):
        super().__init__(**kwargs)
        self.spin = spin

    def getColor(self, context:EvaluationContext ) -> RGB:
        spinValue = context.valueOf( self.spin )
        wheelValue = rainbowio.colorwheel( spinValue )
        rv = RGB.fromNeoPixelInt( wheelValue )
        if self.enableDbgOut:  self.dbgOut( 'getColor rv=%r,  spin=%r, wheel=%X', rv, spinValue, wheelValue )
        return rv

class PipeInputSource(InputSource):
    def __init__( self, input:Evaluatable, **kwargs ):
        super().__init__(**kwargs)
        self.input = input
        
    def getPipedValue(self, context:EvaluationContext, v:Any ) -> Any:
        raise NotImplemented
    
    def getDerivedValue(self, context:EvaluationContext) -> RGB:
        v = context.valueOf(self.input)
        return self.getPipedValue(context,v)

class Z21Adapted(PipeInputSource):
    def __init__( self, input:Evaluatable, min:Optional[Any]=None,max:Optional[Any]=None,**kwargs ):
        super().__init__(input,**kwargs)
        self._min = min
        self._max = max
        self._span = None if min is None or max is None else max - min
        
        
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
