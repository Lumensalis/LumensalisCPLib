from __future__ import annotations
from math import log
from LumensalisCP.Lights._common import *
from LumensalisCP.IOContext import *
#from LumensalisCP.Main.Expressions import NamedOutputTarget, EvaluationContext
from LumensalisCP.Lights.Pattern import *

from LumensalisCP.Temporal.Oscillator import Sawtooth

#############################################################################
from LumensalisCP.Lights import TestPatternsRL

class PatternRLTest( Pattern, OutputTarget ):
    def __init__(self,
                target:LightGroup, name:Optional[str]=None, 
                a:AnyRGBValue|Evaluatable = 1.0,
                b:AnyRGBValue|Evaluatable = 0.0,
                value:ZeroToOne|Evaluatable = 0.0,
                **kwargs
            ):
        self._onValue = a
        self._offValue = b
        self._value = value
        Pattern.__init__( self, target=target,name=name, **kwargs)
        OutputTarget.__init__(self )

    @property
    def value(self)->ZeroToOne|Evaluatable: return self._value
    
    @property
    def a(self): return  self._onValue
    @a.setter
    def a(self,v):  self._onValue = v
    
    def set( self, value:ZeroToOne, context:EvaluationContext ):
        self._value = value

    def refresh( self, context:EvaluationContext ):
        level = withinZeroToOne( context.valueOf(self._value) )
        target = self.target
        maxPxf = level * target.lightCount
        maxPx = int(maxPxf)
        pxR = maxPxf - maxPx
        
        a = RGB.toRGB( context.valueOf(self._onValue) )
        b = RGB.toRGB( context.valueOf(self._offValue) )
        
        
        for px in range(target.lightCount):
            if px < maxPx:
                v = a 
            elif px > maxPx:
                v = b 
            else:
                v = b.fadeTowards(a, pxR)
            target[px] = v

ABFade = PatternRLTest

class Spinner( OnOffPattern ):
    """ a spinning pattern that wraps around the end of the LightGroup
    """
    def __init__(self,
                target:LightGroup, name:Optional[str]=None, 
                period:TimeInSecondsEval = 0.5,
                tail:ZeroToOne = 0.35,
                **kwargs:Unpack[OnOffPattern]
            ):
        """ a spinning pattern that wraps around the end of the LightGroup

        :param target: group to be controlled
        :type target: LightGroup
        :param name: name of the pattern, defaults to None
        :type name: Optional[str], optional
        :param onValue: value or Evaluatable convertible to RGB
        :type onValue: RGBEvalArg, optional
        :param period: duration of single spin
        :type period: TimeInSecondsEval, optional
        :param tail: length of tail
          
            **0**=no tail, **1.0**=full tail
        :type tail: ZeroToOne, optional
        """
        self._tail = tail
        super().__init__( target=target, **kwargs)
        self.oscillator = Sawtooth( name, period=period )
        

    @property
    def onValue(self): return  self._onValue
    @onValue.setter
    def onValue(self,v):  self._onValue = v
    
    def set( self, value:ZeroToOne, context:EvaluationContext ):
        self._value = value

    def refresh( self, context:EvaluationContext ):
        z2one = self.oscillator.getValue(context)
        target = self.target
        
        onValue = RGB.toRGB( context.valueOf(self._onValue) )
        offValue = RGB.toRGB( context.valueOf(self._offValue) )
        
        rotation = z2one * target.lightCount
        tail = target.lightCount * context.valueOf( self._tail )
        t10 = 10.0 / tail

        for px in range(target.lightCount):
            delta =  divmod( px - rotation, target.lightCount )[1]
            if delta > 0 and delta <= tail:
                delta = delta * (log(delta*t10, 10))
                v = offValue.fadeTowards(onValue, delta/tail)
            else:
                v = offValue 
            target[px] = v

class PatternTemplate(object):
    """ shorthand for creating patterns with consistent options

    :param object: _description_
    :type object: _type_
    """
    def __init__( self, patternClass:Type[Pattern], *args, **kwds ):
        self.patternClass = patternClass
        self.args = args
        self.kwds = kwds
    
    def __call__(self, *args, **kwds ):
        fullArgs = self.args + args
        fullKwds = dict( self.kwds )
        fullKwds.update( kwds )
        return self.patternClass( *fullArgs, **fullKwds )
    
__all__ = [Spinner, PatternTemplate]