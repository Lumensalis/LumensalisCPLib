from ..GCSimpleBench import *

def GC_ArgsKwds():
    

    argPlus = GCTestSet()

    def foo( a:Any ) -> None:
        return None

    def baseline(  a:str, *args:Any ) -> None:
        return None

    def justStr( a:str ) -> None:
        foo(a)
        

    def strOpt1( a:str, b:Optional[Any]=None ) -> None:
        foo(a)

    def strOpt4Any( a:str, b:Optional[Any]=None, c:Optional[Any]=None , d:Optional[Any]=None , **args:Any ) -> None:
        foo(a)

    def strArgs( a:str, *args:Any ) -> None:
        foo(a)

    def strKwds( a:str, **kwargs:Any ) -> None:
        foo(a)

    def strArgsKwds( a:str, *args:Any, **kwargs:Any ) -> None:
        foo(a)


    argPlus.addTester( "argPlus",
            signature = [GCTArg("a",str)],
            baseline = baseline,
            tests=[ 
                    justStr,
                    strOpt1,
                    strOpt4Any,
                    strArgs,
                    strKwds,
                    strArgsKwds,
            ]
        ).addArgs( "easy","hello world"
        ).addArgs( "two","hello", "world"
        ).addArgs( "bKwd", invoke=lambda c: c("hello", b="world")
        )
    

    argPlus.run(cycles=10)
    #print( f"s1 at {s1.tell()}, s2 at {s2.tell()}" )
