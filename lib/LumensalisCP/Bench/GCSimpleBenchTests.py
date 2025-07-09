from .GCSimpleBench import *

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
    tester = GCTester(baseline = lambda a: None )
    tester.addTests( foo=foo,bar=bar,baz=baz
                    )
    
    config = GCTestRunConfig(cycles=10, innerCycles=5,args=[2])
    print( "running..." )
    results = tester.run(config=config)
    results.writeOnScope(sys.stdout)
    
    config.optimizeArgs = True
    tester.run(config=config).writeOnScope(sys.stdout)

#############################################################################

def kwdsBaseline( a=None, b=None, c=None ):
    pass

class KtClass(object):
    
    def __init__( self ):
        pass
    
    def kBar(self,a=None, b=None, c=None ):
        return None

def ktBar( a=None, b=None, c=None ):
    return a + 1

def ktBarABC( a, b, c ):
    return a

def ktBarNone( a=None, b=None, c=None ):
    return None

def ktFoo( a, b=None, c=None ):
    pass

def ktFooBar( a, b=None, c=None ):
    return ktBar( a, b, c )

def ktFooBarK( a, b=None, c=None ):
    return ktBar( a=a, b=b, c=c )
    
def ktFooBarNone( a, b=None, c=None ):    
    return ktBarNone( a, b, c )

def ktFooBarNoneK( a, b=None, c=None ):    
    return ktBarNone( a=a, b=b, c=c )
        

def ktFooBarNoneA( a ):
    return ktBarNone( a )

def ktBaz( *args, **kwds ):
    pass


def ktBazA( *args, **kwds ):
    pass

def ktBazK( **kwds ):
    pass

from LumensalisCP.util.kwCallback import KWCallback

def kwcWrap( name:str|None=None ):
    def wrapper( callable:Callable  ):
        cb = KWCallback(callable,name=name)
        cb.__name__ = cb.name
        return cb

    return wrapper

@kwcWrap(None)
def wktFooBarNoneA( a ):
    return ktBarNone( a )

@kwcWrap(None)
def wktBarABC( a, b, c ):
    return a

@kwcWrap(None)
def wktBarNone( a=None, b=None, c=None ):
    return None

def kwdsTest():
    tester = GCTester(baseline = kwdsBaseline )
    ktc = KtClass()
    tester.addTests(
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
        )
    if 0:
        tester.addTests(
            ktFooBar,
            ktFooBarK,
            ktFooBarNone,
            ktFooBarNoneK,
            ktFooBarNoneA,
            
            ktc.kBar,
            ktFoo=ktFoo,
            
            ktBar=ktBar,
            ktBaz=ktBaz
        )

    print( "\n\nrunning kwdsTest..." )
    outerWriteScope = TargetedWriteScope( sys.stdout )
    outerWriteScope.config.detailed = False
    
    with outerWriteScope.startList(indentItems=True) as writeScope:
        config = GCTestRunConfig(cycles=15, innerCycles=5,optimizeArgs=True)
        
        def run( *args, optimizeArgs=None, **kwds):
            config.args=args if len(args) else None
            config.kwds=kwds if len(kwds) else None
            config.optimizeArgs = config.optimizeArgs if optimizeArgs is None else optimizeArgs
            writeScope.write( tester.run(config=config) )    
        
        run( 1 )
        run( 3.5 )
        run( 5, 6 )
        run( 2, 3, 4 )
        run( 13, c=99 )
        run( 17, b=5, c=99 )
        run( b = 5 )
        
        if 0:
            run( 18, 4 )
            run( "hello world, la la la la la la la", 4 )
         
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
    def iteratedD( l=None, m=2, n=3 ): return iter(l)
    def iteratedA( *args ): return iter(args[0])
    def iteratedAK( *args, **kwds ): return iter(args[0])
    def iteratedlAK( l, *args, **kwds ): return iter(l)
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
                iteratedlAK,
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