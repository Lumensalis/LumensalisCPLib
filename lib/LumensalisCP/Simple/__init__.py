""" common imports for simple (typically single file, no class) projects

Intended to be used as 
```python
from LumensalisCP.Simple import *
main = ProjectManager() 

# configure your project here...

main.launchProject( globals() )
```
more at http://lumensalis.com/ql/h2Start
"""
from __future__ import annotations

import rainbowio
import gc

# pyright: ignore[reportUnusedImport]
# pylint: disable=unused-import,import-error,unused-argument 
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false

from LumensalisCP.ImportProfiler import getImportProfiler
from LumensalisCP.Main.PreMainConfig import pmc_gcManager, pmc_mainLoopControl
pmc_mainLoopControl.sayAtStartup( "beginning import of LumensalisCP.Simple.__init__" )

_saySimpleImport = getImportProfiler( "Simple.__init__" )

def _importCollect() -> None:
    _saySimpleImport( "collecting garbage..." )
    gc.collect()
    
_saySimpleImport( "PreMainConfig")
from LumensalisCP.Main.PreMainConfig import *

import LumensalisCP.Simple
from LumensalisCP.Lights.RGB import *
import LumensalisCP.Identity.Local
import LumensalisCP.Main.Updates
import LumensalisCP.util.kwCallback
import LumensalisCP.Eval.EvaluationContext 
import LumensalisCP.Eval.ExpressionTerm 
_importCollect()
import LumensalisCP.Eval.Terms 
import LumensalisCP.Eval.Evaluatable 
import LumensalisCP.Eval.common
import LumensalisCP.Inputs
import LumensalisCP.Outputs
_importCollect()
import LumensalisCP.IOContext
_importCollect()
import LumensalisCP.Triggers 
from LumensalisCP.Triggers.Timer import addPeriodicTaskDef, addSimplePeriodicTaskDef, PeriodicTimerManager, PeriodicTimer
from LumensalisCP.Triggers.Action import *
from LumensalisCP.Behaviors.Behavior import Behavior, Actor 
from LumensalisCP.Behaviors.Behavior import Behavior as BehaviorClass
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Audio.Effect import *
from LumensalisCP.Demo.DemoCommon import *
from LumensalisCP.Simple.ProjectManager import ProjectManager

_saySimpleImport.parsing()

def getColor( v:AnyRGBValue ) -> RGB:
    """ convert __v__ to an RGB value

    :param v: value to be converted
    :type v: AnyRGBValue
    :return: _description_
    :rtype: RGB
    """
    return RGB.toRGB(v)

class ColorSource(InputSource):
    """ base class for InputSource which provides RGB color values """

    def getColor(self, context:EvaluationContext ) -> RGB:
        raise NotImplementedError
    
    def getDerivedValue(self, context:EvaluationContext) -> RGB:
        return self.getColor(context)


class ColorWheel(ColorSource):
    def __init__( self, spin:Evaluatable[int], **kwargs:Unpack[ColorSource.KWDS] ) -> None:
        """ provides an RGB color which changes as the value of spin changes
        
        :param spin: the value to use for the color wheel, should be between 0 and 255
        """ 
        super().__init__(**kwargs)
        self.spin = spin

    def getColor(self, context:EvaluationContext ) -> RGB:
        with context.subFrame('getColor', self.name ) as activeFrame:
            spinValue = context.valueOf( self.spin )
            activeFrame.snap( "colorwheel" )
            wheelValue = rainbowio.colorwheel( spinValue )
            rv = RGB.fromNeoPixelRGBInt( NeoPixelRGBInt(wheelValue) )
            if self.enableDbgOut:  self.dbgOut( 'getColor rv=%r,  spin=%r, wheel=%X', rv, spinValue, wheelValue )
            return rv

class ColorWheelZ1(ColorSource):
    def __init__( self, spin:Evaluatable[ZeroToOne], **kwargs:Unpack[ColorSource.KWDS] ) -> None:
        """ provides an RGB color which changes as the value of spin changes from 0 to 1
        
        :param spin: the value to use for the color wheel, should be between 0 and 1
        """ 
        super().__init__(**kwargs)
        self.spin = spin
        self._colors = [  
                RGB.fromNeoPixelRGBInt(  rainbowio.colorwheel(x) ) # type: ignore
                for x in range(256) ]  # precompute the colors

    def _getColor(self, val:ZeroToOne ) -> RGB:

        index = max( 0, min(255, int(val * 255)) )
        rv =  self._colors[index]
        if self.enableDbgOut:
            self.dbgOut( 'rv=%r index=%d getColor spin=%r, ', rv, index, val )
        return rv

    def getColor(self, context:EvaluationContext ) -> RGB:
        return self._getColor( context.valueOf( self.spin ))
        
class PipeInputSource(InputSource):
    def __init__( self, inputSource:Evaluatable[Any], **kwargs:Unpack[InputSource.KWDS] ):
        super().__init__(**kwargs)
        assert isinstance(inputSource, Evaluatable), f"PipeInputSource requires an Evaluatable inputSource, not {type(inputSource)}"
        self.inputSource = inputSource

        
    def dependencies(self) -> Iterable[Evaluatable]::  
        for dependency in InputSource.dependencies(self):
            yield dependency
        for dependency in self.inputSource.dependencies():
            yield dependency

    def getPipedValue(self, context:EvaluationContext, v:Any ) -> Any:
        raise NotImplementedError
    
    def getDerivedValue(self, context:EvaluationContext) -> Any:
        if True:
            return self.getPipedValue(context, context.valueOf(self.inputSource))

        with context.subFrame('PipeInputSource.getDerivedValue', self.name ) as activeFrame:
            v = context.valueOf(self.inputSource)
            activeFrame.snap("frameTest")
            with context.subFrame('nestedFrame', self.name ) as nestedFrame:
                nestedFrame.snap("frameSnap")
            activeFrame.snap("getPipedValue")
            rv = self.getPipedValue(context,v)
            activeFrame.snap("return")
        return rv

class Z21Adapted(PipeInputSource):
    def __init__( self, 
                 inputSource:Evaluatable[float],
                 min:Optional[float]=None, 
                 max:Optional[float]=None,
                 autoRange:bool=True, 
                 **kwargs:Unpack[PipeInputSource.KWDS] ) -> None: # pylint: disable=redefined-builtin
        """ adapt the value of inputSource to a range between 0.0 (at min) and 1.0 (at max)
        :param inputSource: the input source to adapt
        :param min: the minimum value, defaults to None (which will use the lowest value seen so far)
        :param max: the maximum value, defaults to None (which will use the highest value seen so far)
        :param autoRange: if True, will automatically adjust the min and max values based on the inputSource value
        """
        super().__init__(inputSource,**kwargs )

        self._autoMin = min is None and autoRange
        if not self._autoMin:
            assert isinstance(min, (int, float)), f"Z21Adapted min must be a number, not {type(min)}"
            self._min:float = float(min)

        self._autoMax = max is None and autoRange
        if not self._autoMax:
            assert isinstance(max, (int, float)), f"Z21Adapted max must be a number, not {type(max)}"
            self._max:float = float(max)
        
        self._span:float|None = None if min is None or max is None else float(max - min)
        self._autoRange = autoRange
        assert autoRange or self._span is not None, "Z21Adapted requires either autoRange or min and max to be set"
        
    def getPipedValue(self, context:EvaluationContext, v:Any ) -> Any:
        """ convert v to a value between 0.0 and 1.0, using the min and max values"""
        if not isinstance(v, (int, float)):
            v= float(v)
        
        if self._span is None:
            if self._autoMin: self._min = v if self._autoMax else min(v, self._max)
            if self._autoMax: self._max = v  if self._autoMin else max(v, self._min)
            assert self._min is not None and self._max is not None, "Z21Adapted requires both min and max to be set"
            assert self._min <= self._max
            self._span = self._max - self._min
        elif v < self._min:
            if not self._autoMin: return 0.0
            self._min = v
            self._span = self._max - self._min
        elif v > self._max:
            if not self._autoMax: return 1.0
            self._max = v
            self._span = self._max - self._min
        
        if self._span == 0: return 0.0
        offset = (v - self._min)
        if self.enableDbgOut:
            self.dbgOut( 'getPipedValue offset=%r,  v=%r,  min=%r,  max=%r', offset, v, self._min, self._max )    
            if offset < 0.0 or offset > self._span:
                self.errOut(f"Z21Adapted: {v} not in range {self._min}..{self._max}")
        return (v - self._min) / self._span

_saySimpleImport.complete(globals())

pmc_mainLoopControl.sayAtStartup( "ending import of LumensalisCP.Simple.__init__ " )
