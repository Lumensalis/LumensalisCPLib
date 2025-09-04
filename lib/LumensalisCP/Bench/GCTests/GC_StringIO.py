from ..GCSimpleBench import *


#import stringio
import io
from LumensalisCP.util.TextIOHelpers import writeIntOnTextIO

def GC_StringIO():
    
    
    s = GCTestSet()

    def baseline(  a:str, b:int ) -> None:
        return None
    
    s1 = io.StringIO(8192) # type: ignore
    s2 = io.StringIO(8192) # type: ignore

    def writeAll(  a:str, b:int ) -> None:
        s1.write(a)
        
    def writeFront(  a:str, b:int ) -> None:
        s2.write( a[:b] )

    def writeMid(  a:str, b:int ) -> None:
        s2.write( a[b:b+1] )
    
    def writeMid2(  a:str, b:int ) -> None:
        s2.write( a[b:b+2] )

    def writeInt(  a:str, b:int ) -> None:
        s2.write( repr(b) )

    def writeIntTIO( a:str, b:int ) -> None:
        writeIntOnTextIO(s2, b)

    def writeClear(  a:str, b:int ) -> None:
        s2.seek(0)

    def write0(  a:str, b:int ) -> None:
        s2.write( a[0] )
    
    def writeZ(  a:str, b:int ) -> None:
        s2.write( a[-1] )
    
    def writeSlow(  a:str, b:int ) -> None:
        for x in range(len(a)):
            s2.write( a[x] )

    if False:
        s.addTester( "StringIOStrings",
            signature = [GCTArg("a",str), GCTArg("b",int)],
            baseline = baseline,
            tests=[ 
                    writeAll,
                    writeFront,
                    writeMid,
                    writeMid2,
                    write0,
                    writeZ,
                    writeSlow,
            ]
        ).addArgs( "easy","hello world",  5
        )



    def getSlice(  a:str, b:int ) -> None:
        v = memoryview(s2)[max(0,s2.tell()-b),s2.tell()]

    def getSliced(  a:str, b:int ) -> None:
        v =  s2[0,s2.tell()]

    def getValue(  a:str, b:int ) -> None:
        v =  s2.getvalue()

    s.addTester( "StringIOInts",
            signature = [GCTArg("a",str), GCTArg("b",int)],
            baseline = baseline,
            tests=[ 
                    writeInt,
                    writeIntTIO,
                    getSlice,
                    getSliced,
                    getValue
            ]
        ).addArgs( "easy","hello world",  5
        )
    
    
    s.run(cycles=10)
    print( f"\ns1 at {s1.tell()}, s2 at {s2.tell()}" )
