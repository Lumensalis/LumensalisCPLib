
import io
import json
from LumensalisCP.util.TextIOHelpers import writeJsonOnTextIO

from ..GCSimpleBench import *


def GC_StringIOJson():
    
    s = GCTestSet()

    class SIJContext( object ):
        def __init__(self):
            self.sioDump = io.StringIO(8192) # type: ignore
            self.sioWrite = io.StringIO(8192) # type: ignore
            self.sioOther = io.StringIO(8192) # type: ignore
        
        

    def baseline(  sji:SIJContext, value:dict[str,Any] ) -> None:
        return None
    
    def testJsonDumps(  sji:SIJContext, value:dict[str,Any] ) -> None:
        sji.sioDump.seek(0)
        sji.sioDump.write(json.dumps(value))
        return None

    def testRepr(  sji:SIJContext, value:dict[str,Any] ) -> None:
        sji.sioOther.write(repr(value))
        return None

    def testWriteJsonOnTextIO(  sji:SIJContext, value:dict[str,Any] ) -> None:
        sji.sioWrite.seek(0)
        writeJsonOnTextIO(sji.sioWrite, value)
        
    def testReset( sji:SIJContext, value:dict[str,Any] ) -> None:
        dVal = sji.sioDump.getvalue().replace(', ', ',').replace(': ', ':')
        wVal = sji.sioWrite.getvalue()[:sji.sioWrite.tell()]
        if dVal != wVal:
            print( f"mismatch dumps:<{dVal}> != writeJsonOnTextIO:<{wVal}>" )

        #sji.sio.truncate()

    sji = SIJContext()
    testData: dict[str, Any] = {
        "key1": "value1",
        "key2": 23,
        "key3": ["value3",42],
        'd1':dict(a=1,b=2,c=3),
    }

    s.addTester( "StringIOJson",
            signature = [GCTArg("sij",SIJContext), GCTArg("value",Any)],
            baseline = baseline,
            tests=[ 
                    testJsonDumps,
                    testWriteJsonOnTextIO,
                    #testRepr,
                    testReset,
            ]
        #).addArgs( "anInt",sji, 99
        ).addArgs( "tuple",sji, (None,True)
        ).addArgs( "aString",sji, "hello world"
        ).addArgs( "aList",sji, [1,2,3,4,5,6]
        ).addArgs( "nestedDict",sji, testData
        )
    
    s.run(cycles=10)
    
