from ..GCSimpleBench import *

from LumensalisCP.Lights.RGB import RGB, Colors
from collections import namedtuple

TupleRgbTest = namedtuple("TupleRgbTest", ["r", "g", "b"] )

def RGBTest():
    
    
    s = GCTestSet()

    def baseline( a:Any, b:int=0 ) -> Any: 
        return None
    
    def toRgb(  a:Any, b:int=0 ) -> RGB:
        return RGB.toRGB(a)
        
    def toRgbEx(  a:Any, b:int=0 ) -> RGB:
        try:
            return RGB.toRGB(a)
        except Exception as e:
            print(f"Error converting a={a} to RGB: {e}")
            return RGB(0, 0, 0)


    def fadeRgb(  a:Any, b:int=0 ) -> RGB:
        v = RGB.toRGB(a)
        #print(f"Fade {a} towards {Colors.WHITE} by {b}")
        return v.fadeTowards(Colors.WHITE, 0.77)
    
    def intRgb(  a:Any, b:int=0 ) -> RGB:
        v = RGB( b, b+1, b+2 )
        return v

    def tupleRgbTest(  a:Any, b:int=0 ) -> TupleRgbTest:
        v = TupleRgbTest( b, b+1, b+2 )
        return v

    assert RGB.Convertors.supportsType(str)

    s.addTester( "rgb",
            signature = [GCTArg("a",Any), GCTArg("b",int)],
            baseline = baseline,
            tests=[
                    toRgb,
                    toRgbEx,
                    fadeRgb,
                    intRgb,
                    tupleRgbTest,
            ]
        ).addArgs( "hexstr",  "#FF0000", 0  
        ).addArgs( "colorstr",  "BLUE", 0  
        ).addArgs( "ColorsCONST", Colors.BLUE 
        ).addArgs( "tuple", (0,0.5,1)
        ).addArgs( "int", 0x00FF33
        )

    s.run()
    
