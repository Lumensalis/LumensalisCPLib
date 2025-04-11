from LumensalisCP.Lights.LightBase import *

#############################################################################
class ProxyRGBLightsSource( LightSourceBase ):
    def __init__( self,source:LightGroupBase, name:str|None = None, **kwds ):
        self.__lights:List[ProxyRGBLight] = []
        super().__init__( 
                         name = name or f"{self.__class__.__name__}({source.name})",
                         lights = self.__lights, 
                         **kwds
                         )
        for light in source.lights:
            self.__lights.append( self.makeProxy( len(self.__lights), light ) )
    
    def makeProxy(self, index:int, light:LightBase ):
        return ProxyRGBLight( self, index, light )

    def recalculateForwardValue( self, light:"ProxyRGBLight", context: UpdateContext = None  ):
        raise NotImplemented

#############################################################################
        
class ProxyRGBLight( RGBLightBase ):

    def __init__(self, source:"ProxyRGBLightsSource", index:int, light:LightBase ):
        super().__init__(source=source, index=index)
        self.__value = light.getLightValue().asRGB #RGB(0,0,0)
        self.__forwardValue = self.__value
        self.__forwardTarget = light
        
        
    @property
    def value(self): return self.getValue()
    
    def getValue(self, context: UpdateContext = None ) -> AnyLightValue:
        return self.__value
    
    def getLightValue(self)-> LightValueBase: 
        return LightValueRGB( self.__value )
    
    @property
    def lightType(self): return  LightType.LT_RGB

    def recalculateForwardValue( self, context: UpdateContext = None  ):
        return self.source.recalculateForwardValue( self, context  )
        
    def setValue(self,value:AnyLightValue, context: UpdateContext = None ):
        if context is not None:
            value = context.valueOf(value)
        v = LightValueRGB.toRGB(value)
        if v != self.__value:
            self.__value = v
            fv = self.recalculateForwardValue( context )
            if fv != self.__forwardValue:
                self.__forwardValue = fv
                self.__forwardTarget.setValue( fv, context )
            
            

    
 
class DimmedLightsSource( ProxyRGBLightsSource ):
    def __init__( self,source:LightGroupBase, brightness=1.0, **kwargs ):
        super().__init__(source,**kwargs)
        self.__brightness = brightness
        self.__black = RGB()
        
        
    def recalculateForwardValue( self, light:"ProxyRGBLight", context: UpdateContext = None ):
        v = light.value
        return self.__black.fadeTowards( v, self.__brightness )
