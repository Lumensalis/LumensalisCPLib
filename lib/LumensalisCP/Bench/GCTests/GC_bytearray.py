from ..GCSimpleBench import *


#import stringio
import io
#from LumensalisCP.util.TextIOHelpers import writeIntOnTextIO, writeJsonTagValOnTextIO
from ulab import numpy as np

class Uint8Buffer(np.ndarray):
    def init(self, data:Any):
        super().__init__(data, dtype=np.uint8)

_EMPTY=[]
def GC_bytearray():
    
    
    s = GCTestSet()

    class SIJContext( object ):
        def __init__(self):
            self.data = bytearray(8192) # type: ignore
            self.data2 = Uint8Buffer( [0 for _ in range(8192)] ) # type: ignore

        def reset(self):
            #self.data[:] = _EMPTY
            self.data = bytearray()
            self.data2.fill(0)
        
    sji = SIJContext()

    def baseline(  sji:SIJContext, i:int, value:dict[str,Any] ) -> None:
        sji.reset()
        return None
    
    def testStatic(  sji:SIJContext, i:int, value:dict[str,Any] ) -> None:
        sji.reset()
        sji.data.extend( b'23sdsdfsd wasdgs gfsdgsgsg')

    def testStaticTwo(  sji:SIJContext, i:int, value:dict[str,Any] ) -> None:
        sji.reset()
        sji.data.extend( b'GG')        

    def testTwo(  sji:SIJContext, i:int, value:dict[str,Any] ) -> None:
        sji.reset()
        sji.data.extend(i.to_bytes (2,'big') )

    def testTwoRaw(  sji:SIJContext, i:int, value:dict[str,Any] ) -> None:
        sji.reset()
        sji.data.append( (i>>8) & 0xFF )
        sji.data.append( i & 0xFF )

    def testFour(  sji:SIJContext, i:int, value:dict[str,Any] ) -> None:
        sji.reset()
        sji.data.extend( i.to_bytes(4,'big') )

    def testFourRaw(  sji:SIJContext, i:int, value:dict[str,Any] ) -> None:
        sji.reset()
        sji.data.append( (i>>24) & 0xFF )
        sji.data.append( (i>>16) & 0xFF )
        sji.data.append( (i>>8) & 0xFF )
        sji.data.append( i & 0xFF )
        
    def testEight(  sji:SIJContext, i:int, value:dict[str,Any] ) -> None:
        sji.reset()
        sji.data.extend( i.to_bytes(8,'big') )


    sji = SIJContext()
    testData: dict[str, Any] = {
        "key1": "value1",
        "key2": 23,
        "key3": ["value3",42],
        'd1':dict(a=1,b=2,c=3),
    }

    s.addTester( "StringIOJson",
            signature = [GCTArg("sij",SIJContext), GCTArg("i",int), GCTArg("value",Any)],
            baseline = baseline,
            tests=[ 
                    testStaticTwo,
                    testTwo,
                    testTwoRaw,
                    testFour,
                    testFourRaw,
                    testEight,
                    testStatic,
            ]
        #).addArgs( "anInt",sji, 99
        ).addArgs( "tuple",sji, 5, (None,True)
        ).addArgs( "aString",sji, 999, "hello world"
        ).addArgs( "aList",sji, 2345678, [1,2,3,4,5,6]
        #).addArgs( "nestedDict",sji, testData
        )
    
    s.run(cycles=21)