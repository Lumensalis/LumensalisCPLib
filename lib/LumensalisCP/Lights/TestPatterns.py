from LumensalisCP.Lights.Light import *
from LumensalisCP.IOContext import *
#from LumensalisCP.Main.Expressions import NamedOutputTarget, EvaluationContext
from LumensalisCP.Lights.Pattern import *
from random import random as randomZeroToOne, randint
from LumensalisCP.Temporal.Oscillator import Sawtooth

#############################################################################
from . import TestPatternsRL
from math import log

class PatternRLTest( Pattern, OutputTarget ):
    def __init__(self,
                target:LightGroup, name:Optional[str]=None, 
                a:AnyLightValue|Evaluatable = 1.0,
                b:AnyLightValue|Evaluatable = 0.0,
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
        
        a = LightValueRGB.toRGB( context.valueOf(self._onValue) )
        b = LightValueRGB.toRGB( context.valueOf(self._offValue) )
        
        
        for px in range(target.lightCount):
            if px < maxPx:
                v = a 
            elif px > maxPx:
                v = b 
            else:
                v = b.fadeTowards(a, pxR)
            target[px] = v

ABFade = PatternRLTest


class Spinner( Pattern ):
    def __init__(self,
                target:Optional[LightGroup]=None, name:Optional[str]=None, 
                onValue:AnyLightValue = 1.0,
                offValue:AnyLightValue = 0.0,
                period:TimeSpanInSeconds = 0.5,
                tail:ZeroToOne = 0.35,
                **kwargs
            ):
        self._onValue = onValue
        self._offValue = offValue
        self._tail = tail
        super().__init__( target=target,name=name, **kwargs)
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

        onValue = LightValueRGB.toRGB( context.valueOf(self._onValue) )
        offValue = LightValueRGB.toRGB( context.valueOf(self._offValue) )
        
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