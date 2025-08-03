from .GCSimpleBench import *

# typing: ignore

# pyright: reportUnknownVariableType=false,reportUnknownMemberType=false,reportUnknownArgumentType=false,reportUnknownParameterType=false,reportUnknownVariableType=false
# pyright: reportMissingParameterType=false,reportUnusedImport=false,reportUnusedVariable=false
# pyright: reportArgumentType=false,reportUnusedImport=false,reportUnusedVariable=false,reportUnknownLambdaType=false

#############################################################################

def innerFoo( ):
    return 42

def foo(a, w=0):
    return 42

def bar(a, w=0):
    return None
v = 0

def baz(a, w:int=1):
    return v+w
        
def simpleTest():
    s = GCTestSet()
    #tester = GCTester(baseline = lambda a: None )
    s.addTester( "simple",
            signature = [GCTArg("a",Any)],
            baseline =  lambda a: None,
            tests=[ foo,bar,baz ]
        ).addArgs( "two", [2])
    s.run()

#############################################################################

def kwdsBaseline( a:Any=None, b:Any=None, c:Any=None ):
    pass

class KtClass(object):
    
    def __init__( self ):
        pass
    
    def kBar(self,a:Any=None, b:Any=None, c:Any=None ):
        return None

def ktBar( a:Any=None, b:Any=None, c:Any=None ):
    return a + 1 # type: ignore 

def ktBarABC( a:Any, b:Any, c:Any ):
    return a

def ktBarNone( a:Any=None, b:Any=None, c:Any=None ):
    return None

def ktFoo( a, b:Any=None, c:Any=None ):
    pass

def ktFooBar( a:Any, b:Any=None, c:Any=None ):
    return ktBar( a, b, c )

def ktFooBarK( a:Any, b:Any=None, c:Any=None ):
    return ktBar( a=a, b=b, c=c )

def ktFooBarNone( a:Any, b:Any=None, c:Any=None ):
    return ktBarNone( a, b, c )

def ktFooBarNoneK( a:Any, b:Any=None, c:Any=None ):
    return ktBarNone( a=a, b=b, c=c )
        

def ktFooBarNoneA( a:Any ):
    return ktBarNone( a )

def ktBaz( *args:Any, **kwds:Any ):
    pass


def ktBazA( *args:Any, **kwds:Any ):
    pass

def ktBazK( **kwds:Any   ):
    pass

from LumensalisCP.util.kwCallback import KWCallback, KWCallbackArg

def kwcWrap( name:Optional[str]=None ) -> Callable[..., KWCallback]:
    def wrapper( callable:Callable[..., Any]  ) -> KWCallback:
        cb = KWCallback(callable,name=name)
        try:
            # TODO:  callable naming cleanup
            cb.__name__ = cb.name # type: ignore
        except: pass
        return cb

    return wrapper

@kwcWrap(None)
def wktFooBarNoneA( a:Any ):
    return ktBarNone( a )

@kwcWrap(None)
def wktBarABC( a:Any, b:Any, c:Any ) -> Any:
    return a

@kwcWrap(None)
def wktBarNone( a:Any=None, b:Any=None, c:Any=None ):
    return None

#############################################################################

def kwdsSetTest():
    
    s = GCTestSet()

    ktc = KtClass()    
    s.addTester( "kwds",
            baseline = kwdsBaseline,
            signature = [GCTArg("a",int),GCTArg("b",int)],
            tests=[
                ktFoo,
                ktBar,
                ktBarABC,
                ktBaz,
                ktBazA,
                ktBazK,
                ktBarNone,
                wktBarNone,
                wktFooBarNoneA,
                wktBarABC,
            ]
        ).addArgs( "singleInt", 1
        ).addArgs( "singleFloat",3.5
        ).addArgs( "tripleInt", 2, 3, 4 
        ).addArgs( "a c=", 13, c=99 
        ).addArgs( "a b= c=", 17, b=5, c=99 
        ).addArgs(  "b = ", b = 5 
        ).addArgs( "no args"
        )

    s.run()

#############################################################################
from random import random

class ContextTest(object):
    
    def __enter__(self): return self
    
    def __exit__(self, eT, eV, tB):
        pass
    
def setTest():
    
    s = GCTestSet()

    def csBaseline( l ): return l
    
    def copyAndSort( l ):
        l = list(l)
        l.sort()
        return l

    def justSorted( l ): return sorted( l )
    def copyAndSorted( l ): return sorted( list(l) )
    def copyIterated( l ): return list( iter(l) )
    def filteredIterated( l ): return filter( None, iter(l) ) 
    def copyFilteredIterated( l ): return list(filter( None, iter(l) ) )
    def iterated( l ): return iter(l)
    def iteratedD( l:Any=None, m=2, n=3 ): return iter(l)  # type: ignore
    def iteratedA( *args ): return iter(args[0])
    def iteratedAK( *args, **kwds ): return iter(args[0])
    def iteratedLAK( l, *args, **kwds ): return iter(l)
    def listComprehension( l ): return [i for i in l]
    
    ct = ContextTest()
    
    def justSortedWithContext(l ):
        with ct: 
            return sorted( l )
    
    
    s.addTester( "sorting",
            signature = [GCTArg("l",list)],
            baseline = csBaseline,
            tests=[
                copyAndSort,
                copyAndSorted,
                copyIterated,
                copyFilteredIterated,
                filteredIterated,
                justSorted,
                iterated,
                iteratedA,
                iteratedAK,
                iteratedLAK,
                iteratedD,
                listComprehension,
                justSortedWithContext,
            ]
        #).addArgs( "singleInt", [ 1 ]
        #).addArgs( "singleFloat", [ 3.5 ]
        ).addArgs( "tripleInt", [ int(random()*100) for _ in range(10) ]
        )

    s.run()

#############################################################################
import time
def timerTest():
    
    
    s = GCTestSet()

    def baseline( l ): return l
    
    def monotonic( l ):
        return time.monotonic()
    
    def monotonic_ns( l ):
        return time.monotonic_ns()

  
    
    s.addTester( "timing",
            signature = [GCTArg("l",list)],
            baseline = baseline,
            tests=[
                    monotonic,
                    monotonic_ns
            ]
        ).addArgs( "simple", [ 1 ]
        )

    s.run()
    
#############################################################################

def waitForReload():
    print( "\r\nwaiting to reload" )
    while True:
        data = sys.stdin.read()
        print( f"input = {data:r}" )