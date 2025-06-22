from .Light import *
from ..Main.Expressions import NamedOutputTarget, EvaluationContext
from .Pattern import *
from random import random as randomZeroToOne, randint

#############################################################################

#############################################################################
class Rainbow( Pattern ):
    def __init__(self,
                 *args,
                 colorCycle:TimeInSeconds = 1.0,
                 spread:float = 1,
                 **kwargs
            ):
        self.__colorCycle = colorCycle
        self.__colorCycleWhenOffset = 0
        self.__latestCycleWhen = 0
        self.spread = spread
        super().__init__(*args,**kwargs)

    @property
    def colorCycle(self): return self.__colorCycle
    
    @colorCycle.setter
    def colorCycle( self, newCycle ):
        priorOffset = self.__colorCycleWhenOffset
        priorCycle = self.__colorCycle
        newWhen = priorWhen = self.__latestCycleWhen
        '''
        A = ((priorWhen+priorOffset) / priorCycle)
        B = ((newOffset+newWhen) / newCycle)
        
        ((newOffset+newWhen) / newCycle) = ((priorWhen+priorOffset) / priorCycle) 
        newOffset+newWhen = ((priorWhen+priorOffset) / priorCycle) * newCycle
        newOffset = (((priorWhen+priorOffset) / priorCycle) * newCycle) - newWhen
        '''
        self.__colorCycleWhenOffset = (((priorWhen+priorOffset) / priorCycle) * newCycle) - newWhen
        self.__colorCycle = newCycle
    
    def refresh( self, context:UpdateContext ):
        when = self.offsetWhen( context )
        self.__latestCycleWhen = when
        cc = context.valueOf(self.colorCycle)
        #print( f"cc = {cc} from {self.colorCycle}")
        A = (when + self.__colorCycleWhenOffset) / max(0.001,context.valueOf(self.colorCycle))
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
class Gauge( Pattern, NamedOutputTarget ):
    def __init__(self,
                target:LightGroup=None, name:str=None, 
                onValue:AnyLightValue = 1.0,
                offValue:AnyLightValue = 0.0,
                value:ZeroToOne = 0.0,
                **kwargs
            ):
        self.__onValue = onValue
        self.__offValue = offValue
        self.__value = value
        super().__init__( target=target,name=name, **kwargs)
        NamedOutputTarget.__init__(self, name=name )

    @property
    def value(self)->ZeroToOne: return self.__value
    
    @property
    def onValue(self): return  self.__onValue
    @onValue.setter
    def onValue(self,v):  self.__onValue = v
    
    def set( self, value:ZeroToOne, context:EvaluationContext ):
        self.__value = value

    def refresh( self, context:UpdateContext ):
        level = withinZeroToOne( context.valueOf(self.__value) )
        target = self.target
        maxPxf = level * target.lightCount
        maxPx = int(maxPxf)
        pxR = maxPxf - maxPx
        
        onValue = LightValueRGB.toRGB( context.valueOf(self.__onValue) )
        offValue = LightValueRGB.toRGB( context.valueOf(self.__offValue) )
        
        
        for px in range(target.lightCount):
            if px < maxPx:
                v = onValue 
            elif px > maxPx:
                v = offValue 
            else:
                v = offValue.fadeTowards(onValue, pxR)
            target[px] = v

#############################################################################

class Blink( PatternGenerator ):
    def __init__(self,
                 *args,
                 onTime:TimeInSeconds = 1.0,
                 offTime:TimeInSeconds = 1.0,
                 onValue:AnyLightValue = 1.0,
                 offValue:AnyLightValue = 0.0,
                 intermediateRefresh:TimeInSeconds|None=None,
                 **kwargs
            ):
        self.onTime = onTime
        self.offTime = offTime
        self.onValue = onValue
        self.offValue = offValue
        self.intermediateRefresh = intermediateRefresh
        super().__init__(*args,**kwargs)
        
    def regenerate(self, context:UpdateContext):
        yield PatternGeneratorSharedStep( self.onTime, self.onValue, intermediateRefresh=self.intermediateRefresh )
        yield PatternGeneratorSharedStep( self.offTime, self.offValue, intermediateRefresh=self.intermediateRefresh )

#############################################################################

class Random( PatternGenerator ):
    def __init__(self,
                 *args,
                 duration:TimeInSeconds = 1.0,
                 intermediateRefresh:TimeInSeconds = 0.1,
                 brightness:ZeroToOne = 1,
                 **kwargs
            ):
        self.duration = duration
        self.intermediateRefresh:TimeInSeconds = intermediateRefresh
        self.__brightness = brightness
        super().__init__(*args,**kwargs)

    def _generateRandomValues(self, context:UpdateContext):
        rChannelBrightness = int( 0xFF * self.__brightness )
        def rChannel(): return randint(0,rChannelBrightness)
        def randomRGB(): return rChannel() + (rChannel() << 8) + (rChannel() << 16) 
        values = []
        for x in range(self.target.lightCount):
            lightType = self.target[x].lightType
            if lightType == LightType.LT_RGB:
                values.append( randomRGB() )
            elif lightType == LightType.LT_SINGLE_DIMMABLE:
                values.append( randomZeroToOne() )
            else:
                values.append( randomZeroToOne() >= 0.5 )
                
        return values
    
    def regenerate1(self, context:UpdateContext):
        
        yield PatternGeneratorSharedStep(  self.duration, LightValueNeoRGB.randomRGB(brightness=self.__brightness) )
        
    def regenerate(self, context:UpdateContext):
        startValues = self._generateRandomValues(context)
        endValues = self._generateRandomValues(context)
        
        #print(f"Random {self.duration} : {startValues} / {endValues}")
        yield MultiLightPatternStep( self.duration, starts=startValues, ends=endValues )


#############################################################################
import LumensalisCP.Main.Expressions as xm

def prepRGBValue( value ):
    if (
            isinstance( value, xm.ExpressionTerm ) or
            isinstance( value, xm.Expression ) or
            callable(value)
    ):
        return value
    return LightValueRGB.toRGB( value )
    
        
class Cylon2( PatternGenerator ):
    def __init__(self,
                 *args,
                 sweepTime:TimeInSeconds = 1.0,
                 onValue:AnyLightValue = 1.0,
                 offValue:AnyLightValue = 0.0,
                 intermediateRefresh:TimeInSeconds = 0.1,
                 dimRatio:ZeroToOne = 0.7,
                 **kwargs
            ):
        self.__sweepTime = sweepTime
        self.onValue = prepRGBValue( onValue )
        self.offValue = prepRGBValue( offValue )
        self.__dimRatio = dimRatio
        self.intermediateRefresh:TimeInSeconds = intermediateRefresh
        super().__init__(*args,**kwargs)

    @property
    def sweepTime(self) ->TimeInSeconds: return self.__sweepTime
    
    @sweepTime.setter
    def sweepTime(self,sweep:TimeInSeconds):
        self.dbgOut( 'sweep changed to %r', sweep )
        self.__sweepTime = sweep
    
    def regenerate(self, context:UpdateContext):
        with context.subFrame(f'regenerate-{self.name}') as frame:
            sweepStepTime = self.__sweepTime / (self.target.lightCount*2-2)
            lightCount = self.target.lightCount

            
            prior = [ context.valueOf(light.value) for light in self.target.lights ]
            #print( f"prior = { LightValueNeoRGB.formatNeoRGBValues( prior)}" )
            offRGB = LightValueRGB.toRGB( context.valueOf( self.offValue ) )
            def dimmed(index):
                #return self.offValue
                was = LightValueRGB.toRGB(prior[index])
                faded = was.fadeTowards(offRGB, self.__dimRatio )
                return  faded.toNeoPixelInt()
                
            for index in range( self.target.lightCount ):
                onValue = LightValueRGB.toRGB(context.valueOf(self.onValue))
                startValues = [(onValue if i2 == index else dimmed(i2)) for i2 in range(self.target.lightCount) ]
                endValues =startValues
                prior = startValues
                
                yield MultiLightPatternStep( self.__sweepTime/lightCount, starts=startValues, ends=endValues )

            for index in range( max(0, self.target.lightCount-2), 0, -1 ):
                onValue = context.valueOf(self.onValue)
                startValues = [(onValue if i2 == index else dimmed(i2)) for i2 in range(self.target.lightCount) ]
                endValues =startValues
                prior = startValues
                
                yield MultiLightPatternStep( self.__sweepTime/lightCount, starts=startValues, ends=endValues )

#############################################################################

class CylonPatternStep(PatternGeneratorSharedStep):
    def __init__(self, index:int = 0, up:bool=True, *args, **kwds ):
        super().__init__(*args, **kwds)
        self._index = index
        self._up = up
        
    
    def startValue( self, index, context:UpdateContext ):
        return context.valueOf( self._startValue if index == self._index else self._endValue )
    
    def endValue( self, index, context:UpdateContext ):
        return context.valueOf( self._startValue if index == self._index else self._endValue )

    def intermediateValue( self, index, progression:ZeroToOne, context:UpdateContext ):
        if index == self._index: return self.startValue(index,context)
        iOffset = self._index - index if self._up else index - self._index
        if iOffset > 0:
            return self._startValue + (self._endValue - self._startValue) * (progression/iOffset)
        else:
            return self._endValue

#############################################################################

class Cylon( PatternGenerator ):
    def __init__(self,
                 *args,
                 sweepTime:TimeInSeconds = 1.0,
                 onValue:AnyLightValue = 1.0,
                 offValue:AnyLightValue = 0.0,
                 intermediateRefresh:TimeInSeconds = 0.1,
                 **kwargs
            ):
        self.sweepTime = sweepTime
        self.onValue = onValue
        self.offValue = offValue
        self.__movingUp = True
        self.intermediateRefresh:TimeInSeconds = intermediateRefresh
        super().__init__(*args,**kwargs)

        
    def regenerate(self, context:UpdateContext):
        lightCount = self.target.lightCount
        sweepStepTime = self.sweepTime / self.target.lightCount
        if( self.__movingUp ):
            self.__movingUp = False
            for index in range( self.target.lightCount-1 ):
                yield CylonPatternStep( index, up=True,
                    duration=self.sweepTime / lightCount, intermediateRefresh=self.intermediateRefresh, 
                    startValue = self.onValue, endValue = self.offValue  )
        else:
            self.__movingUp = True
            index = self.target.lightCount-1
            while index > 0:
                yield CylonPatternStep( index, up=False,
                    duration=sweepStepTime, intermediateRefresh=self.intermediateRefresh, 
                    startValue = self.onValue, endValue = self.offValue  )


                index -= 1

#############################################################################

