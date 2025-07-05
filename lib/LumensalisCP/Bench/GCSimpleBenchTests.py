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
    outerWriteScope = TargettedWriteScope( sys.stdout )
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
         

def waitForReload():
    print( "\r\nwaiting to reload" )
    while True:
        data = sys.stdin.read()
        print( f"input = {data:r}" )