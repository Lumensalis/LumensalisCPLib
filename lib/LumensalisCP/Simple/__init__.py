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

# pyright: ignore[reportUnusedImport]

from LumensalisCP.Demo.DemoCommon import *
from LumensalisCP.Lights.RGB import *
from LumensalisCP.Main.Manager import MainManager
from LumensalisCP.Triggers.Action import Action
from LumensalisCP.Main.PreMainConfig import *
from LumensalisCP.Behaviors.Behavior import Behavior, Actor 


def ProjectManager( ) -> MainManager:
    """ return the MainManager for a new simple project 
```python
from LumensalisCP.Simple import *
main = ProjectManager()

# configure your project here...

main.launchProject( globals() )
```
see http://lumensalis.com/ql/h2Main
"""
    return  MainManager.initOrGetManager()

def getColor( v:AnyRGBValue ) -> RGB:
    """ convert __v__ to an RGB value

    :param v: value to be converted
    :type v: AnyRGBValue
    :return: _description_
    :rtype: RGB
    """
    return RGB.toRGB(v)

DoArg:TypeAlias = Union[Callable[...,Any],KWCallback,Behavior]

def do( cb:DoArg, *args:Any, **kwds:StrAnyDict ):
    """ create an Action : see see http://lumensalis.com/ql/h2Actions"""
    return Action.makeCallback( cb, *args, **kwds )

def doDbg( cb:DoArg, *args:Any, **kwds:StrAnyDict ):
    return Action.makeDbgCallback( cb, *args, **kwds )

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
        spinValue = context.valueOf( self.spin )
        wheelValue = rainbowio.colorwheel( spinValue )
        rv = RGB.fromNeoPixelRGBInt( NeoPixelRGBInt(wheelValue) )
        if self.enableDbgOut:  self.dbgOut( 'getColor rv=%r,  spin=%r, wheel=%X', rv, spinValue, wheelValue )
        return rv

class PipeInputSource(InputSource):
    def __init__( self, inputSource:Evaluatable[Any], **kwargs:Unpack[InputSource.KWDS] ):
        super().__init__(**kwargs)
        self.inputSource = inputSource
        
    def getPipedValue(self, context:EvaluationContext, v:Any ) -> Any:
        raise NotImplementedError
    
    def getDerivedValue(self, context:EvaluationContext) -> RGB:
        v = context.valueOf(self.inputSource)
        return self.getPipedValue(context,v)

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
