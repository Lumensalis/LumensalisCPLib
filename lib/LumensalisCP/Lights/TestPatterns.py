from .Light import *
from LumensalisCP.IOContext import *
#from ..Main.Expressions import NamedOutputTarget, EvaluationContext
from .Pattern import *
from random import random as randomZeroToOne, randint
from LumensalisCP.Temporal.Oscillator import Sawtooth

#############################################################################
from . import TestPatternsRL
from math import log

class PatternRLTest( Pattern, NamedOutputTarget ):
    def __init__(self,
                target:LightGroup=None, name:str=None, 
                onValue:AnyLightValue = 1.0,
                offValue:AnyLightValue = 0.0,
                value:ZeroToOne = 0.0,
                **kwargs
            ):
        self._onValue = onValue
        self._offValue = offValue
        self._value = value
        super().__init__( target=target,name=name, **kwargs)
        NamedOutputTarget.__init__(self, name=name )

    @property
    def value(self)->ZeroToOne: return self._value
    
    @property
    def onValue(self): return  self._onValue
    @onValue.setter
    def onValue(self,v):  self._onValue = v
    
    def set( self, value:ZeroToOne, context:EvaluationContext ):
        self._value = value

    def refresh( self, context:UpdateContext ):
        level = withinZeroToOne( context.valueOf(self._value) )
        target = self.target
        maxPxf = level * target.lightCount
        maxPx = int(maxPxf)
        pxR = maxPxf - maxPx
        
        onValue = LightValueRGB.toRGB( context.valueOf(self._onValue) )
        offValue = LightValueRGB.toRGB( context.valueOf(self._offValue) )
        
        
        for px in range(target.lightCount):
            if px < maxPx:
                v = onValue 
            elif px > maxPx:
                v = offValue 
            else:
                v = offValue.fadeTowards(onValue, pxR)
            target[px] = v

class Spinner( Pattern ):
    def __init__(self,
                target:LightGroup=None, name:str=None, 
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

    def refresh( self, context:UpdateContext ):
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
