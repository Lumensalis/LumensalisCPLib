from ..GCSimpleBench import *


#import stringio
import io

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

    def write0(  a:str, b:int ) -> None:
        s2.write( a[0] )
    
    def writeZ(  a:str, b:int ) -> None:
        s2.write( a[-1] )
    
    def writeSlow(  a:str, b:int ) -> None:
        for x in range(len(a)):
            s2.write( a[x] )

    s.addTester( "StringIO",
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

    s.run(cycles=10)
    print( f"s1 at {s1.tell()}, s2 at {s2.tell()}" )
