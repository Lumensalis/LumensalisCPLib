from LumensalisCP.Lights.Light import *

#############################################################################
class ProxyRGBLightsSource( LightSource ):
    
    def __init__( self,source:LightGroup, name:str|None = None, **kwds ):
        self.__lights:List[ProxyRGBLight] = []
        super().__init__( 
                         name = name or f"{self.__class__.__name__}({source.name})",
                         lights = self.__lights, 
                         **kwds
                         )
        for light in source.lights:
            self.__lights.append( self.makeProxy( len(self.__lights), light ) )
    
    def makeProxy(self, index:int, light:Light ):
        return ProxyRGBLight( self, index, light )

    def recalculateForwardValue( self, light:"ProxyRGBLight", context: UpdateContext = None  ):
        raise NotImplementedError


#############################################################################
        
class ProxyRGBLight( RGBLight ):

    def __init__(self, source:"ProxyRGBLightsSource", index:int, light:Light ):
        super().__init__(source=source, index=index)
        self.__value:RGB = light.getLightValue().asRGB #RGB(0,0,0)
        self.__forwardValue = self.__value
        self.__forwardTarget = light
        
        
    def getRGB(self):
        return self.__value
    @property
    def value(self): return self.getValue()
    
    def getValue(self, context: UpdateContext = None ) -> AnyRGBValue:
        return self.__value
    
    def getLightValue(self)-> LightValueBase: 
        return LightValueRGB( self.__value )
    
    @property
    def lightType(self): return  LightType.LT_RGB

    def recalculateForwardValue( self, context: UpdateContext = None  ):
        return self.source.recalculateForwardValue( self, context  )
        
    def setValue(self,value:AnyRGBValue, context: UpdateContext = None ):
        if context is not None:
            value = context.valueOf(value)
        v = RGB.toRGB(value)
        if v != self.__value:
            self.__value = v
            fv = self.recalculateForwardValue( context )
            if fv != self.__forwardValue:
                self.__forwardValue = fv
                self.__forwardTarget.setValue( fv, context )
            
            

class ProxyRGBLightsCallbackSource( ProxyRGBLightsSource ):
    def __init__( self,source:LightGroup, cb:Callable = None, **kwargs ):
        super().__init__(source,**kwargs)
        self.__cb = cb

    def recalculateForwardValue( self, light:"ProxyRGBLight", context: UpdateContext = None ):
        return self.__cb(light=light,context=context)

class DimmedLightsSource( ProxyRGBLightsSource ):
    def __init__( self,source:LightGroup, brightness=1.0, **kwargs ):
        super().__init__(source,**kwargs)
        self.__brightness = brightness
        self.__black = RGB()
        
        
    def recalculateForwardValue( self, light:"ProxyRGBLight", context: UpdateContext = None ):
        v = light.value
        return self.__black.fadeTowards( v, self.__brightness )
